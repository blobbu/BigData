from hdfs import InsecureClient
from kafka import KafkaConsumer
import json
import base64
from utils.kafka_logging import KafkaHandler
import os
import logging

logger_name = f'binary_to_hdfs|{os.getpid()}'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
#fh = logging.FileHandler('binary_to_hdfs.log')
#fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
kh = KafkaHandler(os.environ["BOOTSTRAP_SERVERS"].split(','), os.environ["TOPIC_LOGS"], identifier=logger_name)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
ch.setFormatter(formatter)
#logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(kh)




def main():
    kafka_consumer = KafkaConsumer(group_id=os.environ["GENERIC_GROUP"],
                            bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"].split(','),
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                            auto_offset_reset='earliest',
                            max_poll_records=1,
                            #enable_auto_commit=False # only for testing, makes using multiple consumer impossible
                            )
    kafka_consumer.subscribe(pattern=f'{os.environ["TOPIC_SAMPLE_BINARY_BASE"]}-*')
    hdfs_client = InsecureClient(os.environ["HDFS_CONNECTION"])
    for message in kafka_consumer:
        logger.info(f'Received message: Topic:{message.topic} Partition:{message.partition} Offset:{message.offset} Key:{message.key}')
        hdfs_client.write(f'/user/root/{message.value["file_type"]}/{message.value["signature"]}/{message.value["sha256"]}', data=base64.b64decode(message.value['file']), overwrite=True)

if __name__ == "__main__":
    main()