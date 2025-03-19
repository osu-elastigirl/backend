import json
from elasticsearch import Elasticsearch

# connects to index test1
es = Elasticsearch(
  "http://localhost:9200",
  api_key="" # need local API key
)
# API key should have cluster monitor rights
# print(es.info())

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
