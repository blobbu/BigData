from py2neo import Graph
from pymongo import MongoClient
import json
from bson.json_util import dumps

NEO4J_USER = "neo4j"
NEO4J_PORT = "7474"
NEO4J_USER_IP = '10.7.38.65'

# match (a) -[r] -> () delete a, r
#  match (a) delete a
# MATCH (f:File) RETURN f.md5, size((f)-[:IP]->()) as score ORDER BY score DESC limit 20

# MATCH (node:FileSize)
# WHERE node.filesize > 1000
# WITH collect(node) AS nodes
# // compute over relationships of all types
# CALL apoc.algo.pageRank(nodes) YIELD node, score
# RETURN node, score
# ORDER BY score DESC


def main():
    documents = []

    mongo_client = MongoClient('mongodb://root:root@10.7.38.65:27017')
    col = mongo_client['peframe']['peframe']
    cursor = col.find()

    for doc in cursor:
        new = dumps(doc)
        to_json = json.loads(new)
        documents.append(to_json)

    graph_http = "http://" + NEO4J_USER_IP + ":" + NEO4J_PORT
    new_documents = documents
    graph = Graph(graph_http)
    print(graph)
    res_dict = {"items": new_documents}


    query = """
    WITH {json} AS document 
    UNWIND document.items AS q
    MERGE (m:File {md5:q.hashes.md5, sha1:q.hashes.sha1, sha256:q.hashes.sha256}) 
    FOREACH (node in q | MERGE  (n:`Yara` {id:q.hashes.md5}) ON CREATE SET n = node.yara_plugins[0] 
    MERGE (g:File {md5:q.hashes.md5, sha1:q.hashes.sha1, sha256:q.hashes.sha256})-[:YARA]->(n))
    
    MERGE (file_timestamp:`FileTimestamp` {timestamp: q.peinfo.timestamp })
    MERGE (m)-[:COMPILED]->(file_timestamp) 
    
    FOREACH (peinfobehavior IN q.peinfo.behavior | MERGE (z:Behavior {behavior:peinfobehavior})
    MERGE (m)-[:BEHAVIOR]->(z))
    
    FOREACH (ipaddr IN q.strings.ip | MERGE (ip_adr:Ip {ip:ipaddr})
    MERGE (m)-[:IP]->(ip_adr))
    
    MERGE (file_type:`FileType` {filetype: q.filetype } )
    MERGE (m)-[:FILE_TYPE]->(file_type)
    
    
    MERGE (file_size:`FileSize` {filesize: q.filesize } )
    MERGE (m)-[:FILE_SIZE]->(file_size)
    
    FOREACH (pe_breakpoint IN q.peinfo.breakpoint | MERGE (w:Breakpoint {breakpoint:pe_breakpoint})
    MERGE (m)-[:BREAKPOINT]->(w))
      
    """
    query_2 = """
    WITH {json} AS document 
    UNWIND document.items AS q
    UNWIND [k IN KEYS(q.peinfo.directories.import) | k] AS v
    MERGE (import_f:`Import` {import: v} )
    MERGE (m:File {md5:q.hashes.md5, sha1:q.hashes.sha1, sha256:q.hashes.sha256})-[:IMPORT]->(import_f)
    """

    graph.run(query, json=res_dict)
    graph.run(query_2, json=res_dict)

if __name__ == "__main__":
    main()
