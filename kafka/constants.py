TEST = False
REMOTE = True

GENERIC_GROUP = 'generic-group'
GENERIC_GROUP_2 = 'generic-group'
CASSANDRA_USERNAME = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'
if REMOTE:
    BOOTSTRAP_SERVERS = ['10.7.38.62:9092', '10.7.38.63:9093', '10.7.38.64:9094']
    HDFS_CONNECTION = 'http://namenode:9870'
    CASSANDRA_SERVERS = ['10.7.38.63']
    CASSANDRA_PORT = 9042
else:
    BOOTSTRAP_SERVERS = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
    HDFS_CONNECTION = ''
    CASSANDRA_SERVERS = ['10.7.38.63']
    CASSANDRA_PORT = 9042

if TEST:
    TOPIC_SAMPLE_JSON = 'test-samples-json'
    TOPIC_SAMPLE_EXE = 'test-samples-exe'
    TOPIC_LOGS = 'test-logs'
else:
    TOPIC_SAMPLE_JSON = 'samples-json'
    TOPIC_SAMPLE_EXE = 'samples-exe'
    TOPIC_LOGS = 'logs'