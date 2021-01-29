from elasticsearch import Elasticsearch
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
# from kafka_logging import KafkaHandler
import constants
import os
import logging


def check_index(es, logs_index):
    if es.indices.exists(index=logs_index):
        pass
    else:
        es.indices.create(index=logs_index, ignore=400)


def main():
    es = Elasticsearch(hosts="http://elastic:root@10.7.38.62:9200/")

    logs_index = "kafka_logs_test"
    consumer = KafkaConsumer(constants.TOPIC_LOGS,
                             group_id=constants.GENERIC_GROUP_2,
                             bootstrap_servers=constants.BOOTSTRAP_SERVERS,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                             auto_offset_reset='earliest',
                             max_poll_records=1,
                             enable_auto_commit=True  # only for testing, makes using multiple consumer impossible
                             )

    check_index(es, logs_index)

    for message in consumer:
        print(message)
        es.index(index=logs_index, ignore=400, body=message.value)

        logging.info(
            f'Receivced message: Topic:{message.topic} Partition:{message.partition} Offset:{message.offset} Key:{message.key} Value:{message.value}')


if __name__ == "__main__":
    main()
