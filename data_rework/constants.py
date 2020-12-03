TEST = True
REMOTE = True

GENERIC_GROUP = 'generic-group'
CASSANDRA_USERNAME = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'
if REMOTE:
    BOOTSTRAP_SERVERS = ['10.7.38.65:9092', '10.7.38.65:9093', '10.7.38.65:9094']
    HDFS_CONNECTION = 'http://namenode:9870'
    CASSANDRA_SERVERS = ['10.7.38.65']
    CASSANDRA_PORT = 9042
else:
    BOOTSTRAP_SERVERS = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
    HDFS_CONNECTION = ''
    CASSANDRA_SERVERS = ['10.7.38.65']
    CASSANDRA_PORT = 9042

if TEST:
    TOPIC_SAMPLE_JSON_BASE = 'test-samples-json'
    TOPIC_SAMPLE_BINARY_BASE = 'test-samples-binary'
    TOPIC_LOGS = 'test-logs'
else:
    TOPIC_SAMPLE_JSON_BASE = 'samples-json'
    TOPIC_SAMPLE_BINARY_BASE = 'samples-binary'
    TOPIC_LOGS = 'logs'