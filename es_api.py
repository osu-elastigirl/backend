import json
from elasticsearch import Elasticsearch

# connects to index test1
es = Elasticsearch(
  "http://localhost:9200",
  api_key=""
)
# API key should have cluster monitor rights
# print(es.info())


with open('stocks_data.json', 'r') as file:
    data = json.load(file)


operations = []
action = {"index": {"_index": "test2"}}
operations.append(action)
operations.append(data)
response = es.bulk(index="index_for_python_test", body=operations)

print(es.search(index="test2", q="AMZN"))
