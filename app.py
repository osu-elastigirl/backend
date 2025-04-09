from flask import Flask, request
from ai import get_recommendations, getTickers
import json, flask_cors
import datetime
from services.finnhub_service import get_recommendation_trends, get_company_news
from company_info import fetch_company_info
from fundamental_metrics import price_earnings
import pandas as pd
import elastic

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
def get_description():
    request_data = request.get_json()
    desc = request_data['description']
    print("received description:")
    print(desc)
    all_data = False
    if 'all_data' in request_data:
        all_data = request_data['all_data']
    data = description(desc, all_data)
    return json.dumps(data)

def description(desc, all_data=False):
    response_data, stock_data = process_description(desc)
    tickers_and_rationales = {rec['ticker']: rec['rationale'] for rec in response_data}
    metric_keys = []
    if not all_data:
        for rec in response_data:
            metric_keys+=rec['metric_keys']
        metric_keys = set(metric_keys)
    else:
        metric_keys = list(stock_data[list(tickers_and_rationales.keys())[0]].keys())
    data = []
    for stock in stock_data.keys():
        temp = {key: stock_data[stock][key] for key in metric_keys}
        data.append({'ticker': stock, 'rationale': tickers_and_rationales[stock], 'metrics': temp})
    return data
    
def process_description(description):
    tickers = getTickers(gemini_key, description).parsed
    tickers = [ticker.symbol for ticker in tickers]
    data = get_data(tickers)
    descriptions = get_recommendations(gemini_key, description, tickers, data)
    descriptions = json.loads(descriptions.text)
    tickers = [stock['ticker'] for stock in descriptions]
    data = {ticker: data[ticker] for ticker in tickers}
    return descriptions, data

def get_data(stocks:list):
    
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
        company_info = fetch_company_info(stock)
        all_stock_data[stock].update(company_info)
        all_stock_data[stock]["price_earnings"] = price_earnings(stock)

    elastic.uploadData(all_stock_data, "finnhub_data")
    
    return all_stock_data

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
