from hdfs import InsecureClient
import subprocess
import pymongo
import re
import json
import base64
from PIL import Image
import numpy as np
from io import BytesIO

IMG_SIZE = 200

def sanitize(value):
    if isinstance(value, dict):
        value = {sanitize(k):sanitize(v) for k, v in value.items()}
    elif isinstance(value, list):
        value = [sanitize(v) for v in value]
    elif isinstance(value, str):
        value = re.sub(r"[$.]", "_", value)
    return value


def gen_image(f):
    arr = np.frombuffer(f, dtype='uint8', count=-1, offset=0)
    size = int(np.sqrt(arr.shape[0]))
    if size < IMG_SIZE:
        arr = np.pad(arr, (0, IMG_SIZE**2 - size**2))
        size = IMG_SIZE
    arr = np.reshape(arr[:size**2], (size, size))
    img = Image.fromarray(arr)
    img = img.resize((IMG_SIZE, IMG_SIZE))
    return img



def main():
    hdfs_client = InsecureClient('http://10.7.38.62:9870')
    mongo_client = pymongo.MongoClient('mongodb://root:root@10.7.38.65:27017')
    col = mongo_client['images']['images']
    already_done = set()
    for x in col.find({}, {"sha256"}):
        already_done.add(x['sha256'])
    for path, _, files in hdfs_client.walk('/user/root/exe'):
        for f in files:
            if f not in already_done:
                with hdfs_client.read(path + '/' + f) as inpf:
                    img = gen_image(inpf.read())
                    bytes_arr = BytesIO()
                    img.save(bytes_arr, format='PNG')
                    out = {}
                    out['signature'] = path.split('/')[-1]
                    out['sha256'] = f
                    out['base64'] = base64.b64encode(bytes_arr.getvalue())
                    col.insert_one(out)
    
#dec = base64.decodebytes(sample['base64'])
#img2 = Image.open(BytesIO(dec))
if __name__ == "__main__":
    main()



