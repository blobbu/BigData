from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import csv
import json
import logging
import requests
from io import BytesIO
import pyzipper
from kafka_logging import KafkaHandler
import constants
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import base64
#
#
# NOT WORKING
#
#

logger = logging.getLogger(f'kafka_cassandra|{os.getpid()}')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kafka_cassandra.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
kh = KafkaHandler(constants.BOOTSTRAP_SERVERS, constants.TOPIC_LOGS)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(kh)


def send_cassandra(sha256, signature, file):
    if signature == 'n/a':
        signature = 'unknown'
    
    session = cluster.connect()
    session.set_keyspace('exe_img_url')
    cluster.connect()
    session.execute(""" INSERT INTO exe_file_tab (signature, added_time, exe_file) VALUES  ( %s, now(), %s)""",
                    (signature,
                     file
                     ))


def main():
    consumer = KafkaConsumer(constants.TOPIC_SAMPLE_JSON,
                             group_id=constants.GENERIC_GROUP,
                             bootstrap_servers=constants.BOOTSTRAP_SERVERS,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                             auto_offset_reset='earliest',
                             max_poll_records=1,
                             # enable_auto_commit=False # only for testing, makes using multiple consumer impossible
                             )

    auth_provider = PlainTextAuthProvider(username=constants.CASSANDRA_USERNAME, password=constants.CASSANDRA_PASSWORD)
    cluster = Cluster()
    cluster = Cluster(constants.CASSANDRA_SERVERS, port=constants.CASSANDRA_PORT, auth_provider=auth_provider, protocol_version=4)

    for message in consumer:
        logging.info(
            f'Receivced message: Topic:{message.topic} Partition:{message.partition} Offset:{message.offset} Key:{message.key} Value:{message.value}')
        send_cassandra(message.value['sha256'], message.value['signature'], message.value['file'])

if __name__ == "__main__":
    main()