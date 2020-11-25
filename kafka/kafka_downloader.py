from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import csv
import json
import logging
import threading
import time
import queue
import zipfile
import requests
from io import BytesIO
import pyzipper
import base64


PASSWORD = b'infected'
API_URL = 'https://mb-api.abuse.ch/api/v1/'
HEADERS = {
    'API-KEY': 'bc38fd916d8c6489adec8af14c4c2ca4',
    
}

INPUT_TOPIC = 'samples-json'
OUTPUT_TOPIC = 'samples-exe'

logger = logging.getLogger('kafka_downloader')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kafka_downloader.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)



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
                logger.error(f'Non zip content type! SHA256:{sha256} Content:{r.headers["content-type"]}')
        else:
            logger.error(f'Non 200 response code! SHA256:{sha256} Status:{r.status_code}')
        
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


def send(producer, file_exe, sha256):
    data = {
        'sha256': sha256,
        'base64_file': base64.b64encode(file_exe).decode('utf-8')
    }
    producer.send(OUTPUT_TOPIC, data).add_callback(on_send_success, sha256=sha256).add_errback(on_send_error, sha256=sha256)


def on_send_success(record_metadata, sha256):
    logger.info(f'Success! SHA256: {sha256} Topic:{record_metadata.topic} Partition:{record_metadata.partition} Offset:{record_metadata.offset}')


def on_send_error(e, sha256):
    logger.error(f'Failure! SHA256:{sha256} Error:{e}')

def main():
    consumer = KafkaConsumer(INPUT_TOPIC,
                         group_id='my-group',
                         bootstrap_servers=['10.7.38.65:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         auto_offset_reset='earliest', 
                         enable_auto_commit=False)
    
    producer = KafkaProducer(
        bootstrap_servers=['10.7.38.65:9092'], 
        retries=5,
        value_serializer=lambda x: 
                            json.dumps(x).encode('utf-8'),
        max_request_size=10485760)
    
    for message in consumer:
        logging.info(f'Receivced message: Topic:{message.topic} Partition:{message.partition} Offset:{message.offset} Key:{message.key} Value:{message.value}')
        sha256 = message.value['sha256']
        zipped_file = download_sample(sha256)
        unzipped_file = unzip(zipped_file, sha256)
        send(producer, unzipped_file, sha256)

if __name__ == "__main__":
    main()