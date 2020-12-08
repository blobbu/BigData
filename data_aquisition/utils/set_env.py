import os

TEST = False
REMOTE = False


os.environ['BAZAAR_API_KEY'] = 'bc38fd916d8c6489adec8af14c4c2ca4'
os.environ['GENERIC_GROUP'] = 'generic-group'
os.environ['CASSANDRA_USERNAME'] = 'cassandra'
os.environ['CASSANDRA_PASSWORD'] = 'cassandra'
if REMOTE:
    os.environ['BOOTSTRAP_SERVERS'] = '10.7.38.65:9092 10.7.38.65:9093 10.7.38.65:9094'
    os.environ['HDFS_CONNECTION'] = 'http://namenode:9870'
    os.environ['CASSANDRA_SERVERS'] = ['10.7.38.65']
    os.environ['CASSANDRA_PORT'] = '9042'
else:
    os.environ['BOOTSTRAP_SERVERS'] = 'kafka-1:9092 kafka-2:9093 kafka-3:9094'
    os.environ['HDFS_CONNECTION'] = ''
    os.environ['CASSANDRA_SERVERS'] = '10.7.38.65'
    os.environ['CASSANDRA_PORT'] = '9042'

if TEST:
    os.environ['TOPIC_SAMPLE_JSON_BASE'] = 'test-samples-json'
    os.environ['TOPIC_SAMPLE_BINARY_BASE'] = 'test-samples-binary'
    os.environ['TOPIC_LOGS'] = 'test-logs'
else:
    os.environ['TOPIC_SAMPLE_JSON_BASE'] = 'samples-json'
    os.environ['TOPIC_SAMPLE_BINARY_BASE'] = 'samples-binary'
    os.environ['TOPIC_LOGS'] = 'logs'