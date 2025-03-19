from flask import Flask, request
from ai import get_recommendations, getTickers
import json
import flask_cors
import datetime
from services.finnhub_service import get_recommendation_trends as finnhub_recommendation_trends, get_company_news as finnhub_company_news
from services.alpha_vantage_service import get_stock_data as alpha_stock_data
from services.yahoo_finance_service import get_yahoo_stock_data as yahoo_stock_data

# Set up logging for CORS
flask_cors.logging.getLogger('flask_cors').level = flask_cors.logging.DEBUG

# Initialize Flask app
app = Flask(__name__)
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

# Load API keys from config
config = json.load(open('config.json'))
gemini_key = config['gemini_key']
finnhub_key = config['finnhub_key']
alpha_vantage_key = config['alpha_vantage_key']

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
    """
    Process the user-provided description to find relevant stock tickers
    and retrieve data from APIs.
    """
    tickers = getTickers(gemini_key, description).parsed
    tickers = [ticker.symbol for ticker in tickers]
    all_stock_data = getDataForAllStocks(tickers)
    descriptions = get_recommendations(gemini_key, description, tickers, all_stock_data)
    return descriptions.text

def getDataForAllStocks(tickers):
    """
    Fetch data from both Finnhub and Alpha Vantage for multiple stock tickers.
    """
    all_data = {}
    
    for stock in tickers:
        print(f"Fetching data for {stock}...")

        finnhub_data = getFinnhubData(stock)
        alpha_vantage_data = getAlphaVantageData(stock)
        yahoo_stock_data = getYahooFinanceData(stock)

        all_data[stock] = {
            "finnhub": finnhub_data,
            "alpha_vantage": alpha_vantage_data,
            "yahoo": yahoo_stock_data
        }

    return all_data

def getFinnhubData(stock):
    """
    Fetch recommendation trends and news for a given stock from Finnhub.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"Fetching Finnhub data for {stock}...")
    
    try:
        rec_trends = finnhub_recommendation_trends(finnhub_key, stock)
    except Exception as e:
        print(f"Error fetching recommendation trends for {stock}: {e}")
        rec_trends = []
    
    try:
        news = finnhub_company_news(finnhub_key, stock, from_date=today, to_date=today)
    except Exception as e:
        print(f"Error fetching company news for {stock}: {e}")
        news = []
        
    return {
        "recommendation_trends": rec_trends,
        "company_news": news
    }

def getAlphaVantageData(stock):
    """
    Fetch stock data from Alpha Vantage.
    """
    print(f"Fetching Alpha Vantage data for {stock}...")
    
    try:
        data = alpha_stock_data(alpha_vantage_key, stock)
        return data
    except Exception as e:
        print(f"Error fetching Alpha Vantage data for {stock}: {e}")
        return {}
    
def getYahooFinanceData(stock):
    """
    Fetch stock data from Yahoo Finance.
    """
    print(f"Fetching Yahoo Finance data for {stock}...")
    
    try:
        data = yahoo_stock_data(stock)
        return data
    except Exception as e:
        print(f"Error fetching Yahoo Finance data for {stock}: {e}")
        return {}

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
