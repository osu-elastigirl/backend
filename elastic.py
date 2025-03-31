import json
from elasticsearch import Elasticsearch

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
def loadData(data:json): 
    operations = []
    action = {"index": {"_index": "stock_data"}}
    operations.append(action)
    operations.append(data)
    response = es.bulk(index="index_for_python_test", body=operations)

# searches elasticsearch given a symbol
def searchElastic(symbol:str):
    result = es.search(index="stock_data", q=symbol)
    return result
