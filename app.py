from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/description', methods=['POST'])
def description():
    request_data = request.get_json()
    description = request_data['description']
    return process_description(description)
    
def process_description(description):
    # Your code here
    pass

if __name__ == '__main__':
    app.run(port=5000,host="0.0.0.0")
