from hdfs import InsecureClient
import json
client = InsecureClient('http://10.7.38.62:9870')
client.write('test.json', json.dumps({"test-key": "test-val"}))


