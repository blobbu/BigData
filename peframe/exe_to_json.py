from hdfs import InsecureClient
import subprocess
import pymongo
import re
import json

def sanitize(value):
    if isinstance(value, dict):
        value = {sanitize(k):sanitize(v) for k, v in value.items()}
    elif isinstance(value, list):
        value = [sanitize(v) for v in value]
    elif isinstance(value, str):
        value = re.sub(r"[$.]", "_", value)
    return value


def main():
    try:
        hdfs_client = InsecureClient('http://10.7.38.62:9870')
        mongo_client = pymongo.MongoClient('mongodb://root:root@10.7.38.65:27017')
        col = mongo_client['peframe']['peframe']
        already_done = set()
        for x in col.find({}, {"hashes.sha256":1}):
            already_done.add(x['hashes']['sha256'])
        for path, _, files in hdfs_client.walk('/user/root/exe'):
            for f in files:
                if f not in already_done:
                    with hdfs_client.read(path + '/' + f) as inpf:
                        with open('/tmp/infected', 'wb') as outf:
                            outf.write(inpf.read())
                    process = subprocess.Popen(['python3.8', '/home/peframe/peframe/peframecli.py', '-j', '/tmp/infected'],
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    if len(stderr) > 0:
                        print('error')
                        print(stderr)
                    else:
                        out = json.loads(stdout)
                        out = sanitize(out)
                        del out['strings']['dump']
                        out['signature'] = path.split('/')[-1]
                        col.insert_one(out)
    except Exception ex:
        print(ex)
    

if __name__ == "__main__":
    main()



