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
from hdfs import InsecureClient

logger_name = f'sample_to_hdfs|{os.getpid()}'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
#fh = logging.FileHandler('sample_to_hdfs.log')
#fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
kh = KafkaHandler(os.environ["BOOTSTRAP_SERVERS"].split(','), os.environ["TOPIC_LOGS"], identifier=logger_name)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
ch.setFormatter(formatter)
#logger.addHandler(fh)
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
    logger.info('Subscribed to desired topics. Begining processing...')
    hdfs_client = InsecureClient(os.environ["HDFS_CONNECTION"])
    for message in consumer:
        logging.info(
            f'Received message: Topic:{message.topic} \
                Partition:{message.partition} Offset:{message.offset} \
                    Key:{message.key} Value:{message.value}')
        if zipped_file := download_sample(message.value['sha256']):
            if unzipped_file := unzip(zipped_file, message.value['sha256']):
                logger.info(f'Storing in hdfs: {message.value["file_type"]}/{message.value["signature"]}/{message.value["sha256"]}')
        hdfs_client.write(f'/user/root/{message.value["file_type"]}/{message.value["signature"]}/{message.value["sha256"]}', data=unzipped_file, overwrite=True)


if __name__ == "__main__":
    main()
