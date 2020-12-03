from hdfs import InsecureClient
from kafka import KafkaConsumer
import json
import base64
from kafka_logging import KafkaHandler
import constants
import os
import logging

logger = logging.getLogger(f'kafka_hdfs|{os.getpid()}')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kafka_hdfs.log')
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




def main():
    kafka_consumer = KafkaConsumer(group_id=constants.GENERIC_GROUP,
                            bootstrap_servers=constants.BOOTSTRAP_SERVERS,
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                            auto_offset_reset='earliest',
                            max_poll_records=1,
                            #enable_auto_commit=False # only for testing, makes using multiple consumer impossible
                            )
    kafka_consumer.subscribe(pattern=f'{constants.TOPIC_SAMPLE_BINARY_BASE}-*')
    hdfs_client = InsecureClient(constants.HDFS_CONNECTION)
    for message in kafka_consumer:
        logger.info(f'Receivced message: Topic:{message.topic} Partition:{message.partition} Offset:{message.offset} Key:{message.key} Value:{message.value}')
        hdfs_client.write(f'/user/root/{message.value["file_type"]}/{message.value["signature"]}/{message.value["sha256"]}', data=base64.b64decode(message.value['base64_file']))

if __name__ == "__main__":
    main()