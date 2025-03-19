import requests
import json
import datetime

def get_stock_data(key: str, symbol: str) -> dict:
    """
    Fetch daily stock prices (Time Series) for the given stock symbol using Alpha Vantage API.
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": key
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "Time Series (Daily)" in data:
            return data["Time Series (Daily)"]
        else:
            raise ValueError("Invalid response from Alpha Vantage: " + str(data))
    else:
        response.raise_for_status()

# Example usage:
# api_key = "your_alpha_vantage_api_key"
# symbol = "AAPL"
# stock_data = get_stock_data(api_key, symbol)
# print(json.dumps(stock_data, indent=4))
