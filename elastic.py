import json
from elasticsearch import Elasticsearch

"""
username = json.load(open('config.json'))['es_username']
password = json.load(open('config.json'))['es_password']
"""

# connects to Elasticsearch on droplet
ES_HOST = "http://192.241.148.240:9200"
es = Elasticsearch([ES_HOST],
                   basic_auth = ("elastic", "elastigirl123")) # password (elastigirl123) should be removed if repo goes public

'''
# test connection
if (es.ping()):
    print("CONNECTED TO ELASTICSEARCH")
else:
    print("CONNECTION TO ELASTICSEARCH FAILED")
'''

# takes json as input to load into elasticsearch
def uploadData(data:json, index_name): 
    operations = []
    action = {"index": {"_index": index_name}}
    operations.append(action)
    operations.append(data)
    response = es.bulk(index="index_for_python_test", body=operations)

# searches elasticsearch given a symbol
def searchElastic(symbol:str):
    result = es.search(index="stock_data", q=symbol)
    return result
