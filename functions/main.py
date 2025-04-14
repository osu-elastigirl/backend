# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
import requests
import json 
import pandas as pd
import math
import yfinance as yf
from firebase_functions import params
from datetime import datetime

initialize_app()

FINNHUB_API_KEY = params.SecretParam("FINNHUB_API_KEY")

#ADD THE PATH TO YOUR CONFIG FILE!!!!!!
gemini_key = json.load(open('path_to_config.json]'))['gemini_key']

@https_fn.on_request()
def get_description():

    request = https_fn.get_current_request()

    request_data = request.get_json(silent=True)
    if request_data is None: 
        return json.dumps({"error": "Invalid JSON provided"}), 400, {"Content-Type": "application/json"}
    
    desc = request_data.get("description")
    print("received description:")
    print(desc)
    all_data = request_data.get("all_data", False)
    
    data = description(desc, all_data)
    return json.dumps({'data': data}), 200, {"Content-Type": "application/json"}
 
def description(request):
    try:
        request_json = request.get_json(silent=True)
        desc = request_json.get('desc')
        all_data = request_json.get('all_data', False)

        response_data, stock_data = process_description(desc)
        tickers_and_rationales = {rec['ticker']: rec['rationale'] for rec in response_data}

        if not all_data: 
            metric_keys = set()
            for rec in response_data:
                metric_keys.update(rec['metric_keys'])
        else: 
            metric_keys = list(stock_data[list(tickers_and_rationales.keys())[0]].keys())
    
        if not all_data: 
            metric_keys = set()
            for rec in response_data:
                metric_keys.update(rec['metric_keys'])
        else:
            metric_keys = list(stock_data[list(tickers_and_rationales.keys())[0]].keys())
        data = []
        for stock in stock_data.keys():
            temp = {key: stock_data[stock][key] for key in metric_keys}
            data.append({'ticker': stock, 'rationale': tickers_and_rationales[stock], 'metrics': temp})
        return json.dumps(data), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error:": str(e)}), 500, {"Content-type": "application/json"}

def process_description(request):
    try: 
        req_data = request.get_json(silent=True)
        if not req_data or 'description' not in req_data: 
            return json.dumps({"error": "Missing description in request body"}), 400, {"Content-Type": "application/json"}

        description = req_data['description']

        tickers_response = getTickers(gemini_key, description)
        tickers = [ticker.symbol for ticker in tickers_response.parsed]

        data = get_data(tickers)

        recommendations_response = get_recommendations(gemini_key, description, tickers, data)
        descriptions = json.loads(recommendations_response.text)

        tickers = [stock['ticker'] for stock in descriptions]
        filtered_data = {ticker: data[ticker] for ticker in tickers}

        return json.dumps({
        'descriptions': descriptions,
        'data': filtered_data
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e: 
            return json.dumps({"error": f"Failed to process response: {str(e)}"}), 500, {"Content-Type": "application/json"} 
            

def get_data(request):
    
    try: 
        request_json = request.get_json(silent=True)
        stocks = request_json.get("stocks", [])

        if not isinstance(stocks, list):
            return json.dumps({"error": "Expected 'stocks' to be a list"}), 400, {"Content-Type": "application/json"}
        
        today = datetime.date.today().strftime("%Y-%m-%d")
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
            try: 
                company_info = fetch_company_info(stock)
                all_stock_data[stock].update(company_info)
            except Exception as e: 
                print(f"Error fetching company info for {stock}: {e}")
            
            try: 
                all_stock_data[stock]["price_earnings"] = price_earnings(stock)
            except Exception as e: 
                print(f"Error fetching price/earnings for {stock}: {e}")
                all_stock_data[stock]["price_earnings"] = None
        return json.dumps(all_stock_data), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}    

def get_recommendation_trends(request): 
    try: 
        req_data = request.get_json(silent=True)
        symbol = req_data.get("symbol")

        if not symbol: 
            json.dumps({"error": "Symbol parameter is required"}), 400, {"Content-Type": "application/json"}
        
        base_url = "https://finnhub.io/api/v1"
        endpoint = "stock/recommendation"
        url = f"{base_url}/{endpoint}"
        params = { 
            "symbol": symbol, 
            "token": FINNHUB_API_KEY.value
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            return json.dumps(response.json()), 200, {"Content-Type": "application/json"}
        else: 
            return json.dumps({"error": f"Failed to fetch data: {response.text}"}), response.status_code, {"Content-Type": "application/json"}
    
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
    
def get_company_news(request):
    symbol = request.args.get("symbol")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    
    if not all([symbol, from_date, to_date]):
        return json.dumps({"error": "symbol, from_date, and to_date parameters are required"}), 400, {"Content-Type": "application/json"}
        
    # do we need to validate time stamp??

    try: 
        base_url = "https://finnhub.io/api/v1"
        endpoint = "company-news"
        url = f"{base_url}/{endpoint}"
        params = { 
            "symbol": symbol, 
            "from": from_date,
            "to": to_date,
            "token": FINNHUB_API_KEY.value
        }
        response = requests.get(url, params=params)
        response.raise_for_status()

        try: 
            resp_df = pd.DataFrame(response.json()) 
            if not resp_df.empty: 
                ret = resp_df[['headline', 'summary', 'url']]
                return json.dumps(ret.to_dict('records')), 200, {"Content-Type": "application/json"}
            else: 
                return json.dumps([]), 200, {"Content-Type": "application/json"}
                
        except Exception as e: 
            return json.dumps({"error": f"Failed to process response: {str(e)}"}), 500, {"Content-Type": "application/json"}
            
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


def fetch_quarterly(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        data_name = request_json.get("data_name")

        if not ticker or not data_name: 
            return json.dumps({"error": "Missing 'ticker' or 'data_name'"}), 400, {"Content-Type": "application/json"}
        company = yf.Ticker(ticker)
        statement = company.quarterly_balance_sheet
        value = None
        if data_name in statement.index:
            value = float(statement.loc[data_name][0])
            if math.isnan(value):
                return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
            return json.dumps({"value": value}), 200, {"Content-Type": "application/json"}
        print(f"{data_name} does not exist...")
        return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
    
def fetch_quarterly_TTM(request):
    try:
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        data_name = request_json.get("data_name")
        if not ticker or not data_name: 
            return json.dumps({"error": "Missing 'ticker' or 'data_name'"}), 400, {"Content-Type": "application/json"}
        company = yf.Ticker(ticker)
        statement = company.quarterly_cashflow
        value = 0 
        if data_name in statement.index:
            for i in range(4):
                temp = float(statement.loc[data_name][i])
                if math.isnan(temp):
                    return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
                value += temp
            return json.dumps({"value": value}),200, {"Content-Type": "application/json"}
        print(data_name + " does not exists...")
        return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def fetch_quarterly_AVG(request):
    try:
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        data_name = request_json.get("data_name")
        if not ticker or not data_name: 
            return json.dumps({"error": "Missing 'ticker' or 'data_name'"}), 400, {"Content-Type": "application/json"}
        company = yf.Ticker(ticker)
        statement = company.quarterly_cashflow
        value = 0 
        if data_name in statement.index:
            for i in range(4):
                temp = float(statement.loc[data_name][i])
                if math.isnan(temp):
                    return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
                value += temp
            average = value/4 
            return json.dumps({"value": average}),200, {"Content-Type": "application/json"}
        print(data_name + " does not exists...")
        return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
    
def fetch_company_info(request):
    try:
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        if not ticker:
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        company = yf.Ticker(ticker)
        information = company.info

        data = {
            "name": information.get("longName", "N/A"), 
            "description": information.get("longBusinessSummary", "N/A"),
            "sector": information.get("sector", "N/A"),
            "industry": information.get("industry", "N/A"),
            "location": information.get("city", "N/A"),
            "country": information.get("country", "N/A"),
            "founded_year": information.get("yearFounded", "N/A"),
            "website": information.get("website", "N/A"),
        } 
        return json.dumps(data), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def generate_report(request):
    try:
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        
        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        data = { 
            "price_earnings": price_earnings(ticker),
            "price_book": price_book(ticker),
            "total_equity": total_equity(ticker),
            "debt_equity": debt_equity(ticker),
            "free_cash_flow": free_cash_flow(ticker),
            "free_cash_flow_per_share": free_cash_flow_per_share(ticker),
            "4_year_revenue_growth": revenue_growth(ticker),
            "1_yr_daily_BETA": beta(ticker),
        }
        return json.dumps(data), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
    
def fetch(request):
    try:
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")
        
        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        stock = yf.Ticker(ticker)
        prices = stock.history(period ="1d")
        if math.isnan(float(prices['Close'].iloc[0])) or prices.empty: #may not need prices.empty
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        return json.dumps({"value": float(prices['Close'].iloc[0])}), 200, {"Content-type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def price_earnings(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        try:
            pe = fetch(ticker) / fetch_quarterly_TTM(ticker, "Diluted EPS")
            return json.dumps({"value": pe}), 200, {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
        
def price_book(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        
        stock = yf.Ticker(ticker)
        stats = stock.info
        
        return json.dumps({"value": stats.get('priceToBook', 'N/A')}), 200, {"Content-Type": "application/json"}
    
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def total_equity(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        
        try:
            total_assets = fetch_quarterly(ticker, "Total Assets")
            total_liabilties = fetch_quarterly(ticker, "Total Liabilities Net Minority Interest")
            te = total_assets - total_liabilties
            json.dumps({"value": f"{te:.2f}"}), 200, {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def debt_equity(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        try:
            total_debt = fetch_quarterly(ticker, "Total Debt")
            de = total_debt / float(total_equity(ticker))
            return json.dumps({"value": f"{de:.2f}"}), 200, {"Content-Type": "application/json"}

        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def free_cash_flow(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        
        try:
            fcf = fetch_quarterly_TTM(ticker, "Free Cash Flow")
            return json.dumps({"value": f"{fcf:.2f}"}), 200, {"Content-Type": "application/json"}
        
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def free_cash_flow_per_share(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        try:
            fcf = float(free_cash_flow(ticker))
            out_shares = fetch_quarterly_AVG(ticker, "Diluted Average Shares")
            return json.dumps({"value": f"{fcf/out_shares:.2f}"}), 200, {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}

def dividend_yeild(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}

        stock = yf.Ticker(ticker)
        dividend_yield = stock.info['dividendYield']
        try:
            return json.dumps({"value": f"{dividend_yield:.2f}%"}), 200, {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}
        
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
  
def revenue_growth(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}

        rev = []
        avg = 0
        stock = yf.Ticker(ticker)
        income_statement = stock.financials

        for i in range(4):
            rev.append(income_statement.loc['Total Revenue'][i])
        try: 
            for i in range(3):
                avg += (rev[i] / rev[i+1] - 1) * 100      
        except Exception as e:
            return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"} 
        return json.dumps({"value": f"{avg / 3:.2f}%"}), 200, {"Content-Type": "application/json"}
    
    except Exception as e: 
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


def beta(request):
    try: 
        request_json = request.get_json(silent=True)
        ticker = request_json.get("ticker")

        if not ticker: 
            return json.dumps({"error": "Missing 'ticker'"}), 400, {"Content-Type": "application/json"}
        #Get 1 year of given stock prices
        stock_prices = []
        stock = yf.Ticker(ticker)
        history_data = stock.history(period="1y")
        for i in range(len(history_data)):
            stock_prices.append(history_data['Close'][i])

        #Get 1 year of S&P 500 prices
        SnP = []
        sp = yf.Ticker("^GSPC")
        history_data = sp.history(period="1y")  
        for i in range(len(history_data)):
            SnP.append(history_data['Close'][i])
    
        stck = pd.Series(stock_prices)
        indx = pd.Series(SnP)
        stck_returns  = stck.pct_change().dropna()
        indx_returns = indx.pct_change().dropna()
        covariance = stck_returns.cov(indx_returns)
        variance = indx_returns.var()
        beta_value = covariance / variance
        return json.dumps({"value": f"{beta_value:.2f}"}), 200, {"Content-Type": "application/json"}
    except Exception as e: 
        print(e)
        return json.dumps({"value": "N/A"}), 200, {"Content-Type": "application/json"}