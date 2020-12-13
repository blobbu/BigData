from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import csv
import json
import logging
import requests
from io import BytesIO
import pyzipper
from utils.kafka_logging import KafkaHandler
import os
import base64


logger = logging.getLogger(f'hash_to_binary|{os.getpid()}')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('hash_to_binary.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
kh = KafkaHandler(os.environ["BOOTSTRAP_SERVERS"].split(','), os.environ["TOPIC_LOGS"])
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(kh)


PASSWORD = b'infected'
API_URL = 'https://mb-api.abuse.ch/api/v1/'

HEADERS = {
    'API-KEY': os.environ["BAZAAR_API_KEY"],
}



def download_sample(sha256):
    data = {
        'query': 'get_file',
        'sha256_hash': sha256
    }
    zip_file = None
    try:
        r = requests.post(API_URL, data=data, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            if r.headers['content-type'] == 'application/zip':
                zip_file = r.content
            else:
                logger.error(
                    f'Non zip content type! SHA256:{sha256} Content:{r.headers["content-type"]}')
        else:
            logger.error(
                f'Non 200 response code! SHA256:{sha256} Status:{r.status_code}')
    except Exception as err:
        logger.error(f'Download failure! SHA256:{sha256} Error:{err}')
    return zip_file


def unzip(zipped, sha256):
    try:
        filebytes = BytesIO(zipped)
        with pyzipper.AESZipFile(filebytes) as zf:
            zf.setpassword(PASSWORD)
            uzipped_files = {name: zf.read(name) for name in zf.namelist()}
            if len(uzipped_files.keys()) == 1:
                return uzipped_files[next(iter(uzipped_files))]
            else:
                logger.error(f'More than one file in zip! SHA256:{sha256}')
    except Exception as err:
        logger.error(f'Unzip failure! SHA256:{sha256} Error:{err}')


def send(producer, binary_file, sha256, signature, file_type):
    data = {
        'sha256': sha256,
        'file': base64.b64encode(binary_file).decode('utf-8'),
        'signature': signature,
        'file_type': file_type
    }
    producer.send(f'{os.environ["TOPIC_SAMPLE_BINARY_BASE"]}-{file_type}', data).add_callback(on_send_success, sha256=sha256).add_errback(
        on_send_error, sha256=sha256)


def on_send_success(record_metadata, sha256):
    logger.info(
        f'Success! SHA256: {sha256} Topic:{record_metadata.topic}\
             Partition:{record_metadata.partition}\
                  Offset:{record_metadata.offset}')


def on_send_error(e, sha256):
    logger.error(f'Failure! SHA256:{sha256} Error:{e}')


def main():
    consumer = KafkaConsumer(group_id=os.environ["GENERIC_GROUP"],
                             bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"].split(','),
                             value_deserializer=lambda m: json.loads(
                                 m.decode('utf-8')),
                             auto_offset_reset='earliest',
                             max_poll_records=1,
                             # enable_auto_commit=False # only for testing, makes using multiple consumer impossible
                             )
    logger.info('Subscribing to topics...')
    consumer.subscribe(pattern=f'{os.environ["TOPIC_SAMPLE_JSON_BASE"]}-*')
    producer = KafkaProducer(
        bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],
        retries=5,
        value_serializer=lambda x:
        json.dumps(x).encode('utf-8'),
        max_request_size=10485760)
    logger.info('Subscribed to desired topics. Begining processing...')
    for message in consumer:
        logging.info(
            f'Receivced message: Topic:{message.topic} \
                Partition:{message.partition} Offset:{message.offset} \
                    Key:{message.key} Value:{message.value}')
        if zipped_file := download_sample(message.value['sha256']):
            if unzipped_file := unzip(zipped_file, message.value['sha256']):
                send(producer, unzipped_file,
                     message.value['sha256'], message.value['signature'], message.value['file_type'])


if __name__ == "__main__":
    main()
