from flask import Flask, request
from ai import get_recommendations
import json, flask_cors

flask_cors.logging.getLogger('flask_cors').level = flask_cors.logging.DEBUG

app = Flask(__name__)
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})
gemini_key = json.load(open('config.json'))['gemini_key']

@app.route('/')
def hello_world():
    print('Hello, World!')
    return 'Hello, World!'

@app.route('/description', methods=['POST'])
@flask_cors.cross_origin()
def description():
    print(request.get_json())
    request_data = request.get_json()
    description = request_data['description']
    return process_description(description)
    
def process_description(description):
    return get_recommendations(description, gemini_key).text

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')
