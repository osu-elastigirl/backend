from flask import Flask, request
from ai import get_recommendations, getTickers
import json, flask_cors
import datetime
from services.finnhub_service import get_recommendation_trends, get_company_news

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
    request_data = request.get_json()
    description = request_data['description']
    return process_description(description)
    
def process_description(description):
    tickers = getTickers(gemini_key, description).parsed
    tickers = [ticker.symbol for ticker in tickers]
    data = getFinnhubData(tickers)
    descriptions = get_recommendations(gemini_key, description, tickers, data)
    return descriptions.text

def getFinnhubData(stocks:list):
    
    # Use today's date for the news; format: YYYY-MM-DD.
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Dictionary to store all data.
    all_stock_data = {}
    
    for stock in stocks:
        print(f"Fetching data for {stock}...")
        
        try:
            rec_trends = get_recommendation_trends(stock)
        except Exception as e:
            print(f"Error fetching recommendation trends for {stock}: {e}")
            rec_trends = []
        
        try:
            news = get_company_news(stock, from_date=today, to_date=today)
        except Exception as e:
            print(f"Error fetching company news for {stock}: {e}")
            news = []
        
        all_stock_data[stock] = {
            "recommendation_trends": rec_trends,
            "company_news": news
        }
        
    return all_stock_data

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
