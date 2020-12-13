from kafka import KafkaProducer
from kafka.errors import KafkaError
import csv
import json
import logging
import os
from utils.kafka_logging import KafkaHandler

logger = logging.getLogger('csv_to_hash')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('csv_to_hash.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
kh = KafkaHandler(os.environ["BOOTSTRAP_SERVERS"].split(','), os.environ["TOPIC_LOGS"])
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(kh)




def sort_samples(full=True):
    #first_seen_utc","sha256_hash","md5_hash","sha1_hash","reporter","file_name","file_type_guess","mime_type","signature","clamav","vtpercent","imphash","ssdeep","tlsh"
    samples = {}
    if full:
        csv_path = 'full.csv'
    else:
        csv_path = 'recent.csv'
    with open(csv_path) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            if not row[0].startswith("#"):
                if row[6] in samples.keys():
                    samples[row[6]].append({
                        'sha256': row[1],
                        'first_seen': row[0],
                        'reporter': row[4],
                        'file_name': row[5],
                        'file_type': row[6],
                        'signature': row[8]
                    })
                else:
                    samples[row[6]] = [{
                        'sha256': row[1],
                        'first_seen': row[0],
                        'reporter': row[4],
                        'file_name': row[5],
                        'file_type': row[6],
                        'signature': row[8]
                    }]
    return samples


def on_send_success(record_metadata, sha256):
    logger.info(f'Success! SHA256: {sha256} Topic:{record_metadata.topic} Partition:{record_metadata.partition} Offset:{record_metadata.offset}')


def on_send_error(e, sha256):
    logger.error(f'Failure! SHA256:{sha256} Error:{e}')

def main():
    producer = KafkaProducer(
        bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"].split(','), 
        retries=5,
        value_serializer=lambda x: 
                            json.dumps(x).encode('utf-8'))
    logger.info('Reading new csv file...')
    samples = sort_samples()
    logger.info('Uploading hashes...')
    for k, v in samples.items():
        for sample in v:
            producer.send(f'{os.environ["TOPIC_SAMPLE_JSON_BASE"]}-{k}', sample).add_callback(on_send_success, hash=sample['sha256']).add_errback(on_send_error, hash=sample['sha256'])


if __name__ == "__main__":
    main()