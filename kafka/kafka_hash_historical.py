from kafka import KafkaProducer
from kafka.errors import KafkaError
import csv
import json
import logging

KAFKA_TOPIC = 'samples-json'

logger = logging.getLogger('kafka_hash_historical')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kafka_hash_historical.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)




def filter_csv(file_type='exe'):
    #first_seen_utc","sha256_hash","md5_hash","sha1_hash","reporter","file_name","file_type_guess","mime_type","signature","clamav","vtpercent","imphash","ssdeep","tlsh"
    samples = []
    with open('full.csv') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            if not row[0].startswith("#"):
                if row[6] == file_type:                 
                    samples.append({
                        'sha256': row[1],
                        'first_seen': row[0],
                        'reporter': row[4],
                        'file_name': row[5],
                        'file_type_guess': row[6],
                        'mime': row[7],
                        'signature': row[8]
                    })
    return samples


def on_send_success(record_metadata, sha256):
    logger.info(f'Success! SHA256: {sha256} Topic:{record_metadata.topic} Partition:{record_metadata.partition} Offset:{record_metadata.offset}')


def on_send_error(e, sha256):
    logger.error(f'Failure! SHA256:{sha256} Error:{e}')

def main():
    producer = KafkaProducer(
        bootstrap_servers=['10.7.38.65:9092'], 
        retries=5,
        value_serializer=lambda x: 
                            json.dumps(x).encode('utf-8'))

    samples = filter_csv()
    samples.reverse()
    for sample in samples:
        producer.send(KAFKA_TOPIC, sample).add_callback(on_send_success, hash=sample['sha256']).add_errback(on_send_error, hash=sample['sha256'])


if __name__ == "__main__":
    main()
