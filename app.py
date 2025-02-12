from flask import Flask, request
from ai import get_recommendations
import json

app = Flask(__name__)
gemini_key = json.load(open('config.json'))['gemini_key']

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/description', methods=['GET'])
def description():
    print(request)
    request_data = request.get_json()
    description = request_data['description']
    return process_description(description)
    
def process_description(description):
    return get_recommendations(description, gemini_key).text

if __name__ == '__main__':
    app.run(port=5000,host="0.0.0.0")
