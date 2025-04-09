import json
import datetime
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from ai import get_recommendations, getTickers
from services.finnhub_service import get_recommendation_trends, get_company_news
from company_info import fetch_company_info
from fundamental_metrics import price_earnings

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

with open('config.json') as config_file:
    gemini_key = json.load(config_file)['gemini_key']

@app.route('/')
def hello_world():
    return 'Hello, Flask World!'

@app.route('/description', methods=['POST'])
@cross_origin()
def get_description():
    request_data = request.get_json(force=True)
    desc = request_data['description']
    all_data = request_data.get('all_data', False)

    data = asyncio.run(description(desc, all_data))
    return jsonify(data)

def description(desc, all_data=False):
    return asyncio.run(_description(desc, all_data))

async def _description(desc, all_data=False):
    response_data, stock_data = await process_description(desc)
    tickers_and_rationales = {rec['ticker']: rec['rationale'] for rec in response_data}

    if not all_data:
        metric_keys = list({key for rec in response_data for key in rec['metric_keys']})
    else:
        metric_keys = list(stock_data[next(iter(stock_data))].keys())

    data = []
    for stock in stock_data.keys():
        temp = {key: stock_data[stock][key] for key in metric_keys}
        data.append({'ticker': stock, 'rationale': tickers_and_rationales[stock], 'metrics': temp})
    
    return data

async def process_description(description):
    tickers = (await getTickers(gemini_key, description)).parsed
    tickers = [ticker.symbol for ticker in tickers]
    data = await get_data(tickers)
    descriptions = await get_recommendations(gemini_key, description, tickers, data)
    descriptions = json.loads(descriptions.text)
    tickers = [stock['ticker'] for stock in descriptions]
    data = {ticker: data[ticker] for ticker in tickers}
    return descriptions, data

async def get_data(stocks):
    today = datetime.date.today().strftime("%Y-%m-%d")
    all_stock_data = {}

    async def fetch_stock_data(stock):
        try:
            rec_trends = await get_recommendation_trends(stock)
        except Exception as e:
            print(f"Error fetching recommendation trends for {stock}: {e}")
            rec_trends = []
        
        try:
            news = await get_company_news(stock, from_date=today, to_date=today)
        except Exception as e:
            print(f"Error fetching company news for {stock}: {e}")
            news = []

        company_info = await fetch_company_info(stock)
        pe = await price_earnings(stock)

        return stock, {
            "recommendation_trends": rec_trends,
            "company_news": news,
            **company_info,
            "price_earnings": pe
        }

    results = await asyncio.gather(*(fetch_stock_data(stock) for stock in stocks))
    return dict(results)

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)