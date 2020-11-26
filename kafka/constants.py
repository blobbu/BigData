TEST = True



BOOTSTRAP_SERVERS = ['10.7.38.65:9092', '10.7.38.65:9093', '10.7.38.65:9094']
GENERIC_GROUP = 'generic-group'
if TEST:
    TOPIC_SAMPLE_JSON = 'test-samples-json'
    TOPIC_SAMPLE_EXE = 'test-samples-exe'
    TOPIC_LOGS = 'test-logs'
else:
    TOPIC_SAMPLE_JSON = 'samples-json'
    TOPIC_SAMPLE_EXE = 'samples-exe'
    TOPIC_LOGS = 'logs'