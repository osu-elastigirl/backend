import yfinance as yf
import json

def get_yahoo_stock_data(symbol: str) -> dict:
    """
    Fetch daily stock prices for the given stock symbol using Yahoo Finance's `yfinance` library.
    """
    stock = yf.Ticker(symbol)

    # Fetch historical market data (last 30 days)
    hist_data = stock.history(period="1mo", interval="1d")
    
    # Fetch key stock info
    stock_info = stock.info

    # Structure the data similarly to API responses
    stock_data = {
        "symbol": symbol,
        "regularMarketPrice": stock_info.get("currentPrice", None),
        "regularMarketOpen": stock_info.get("open", None),
        "regularMarketDayHigh": stock_info.get("dayHigh", None),
        "regularMarketDayLow": stock_info.get("dayLow", None),
        "fiftyTwoWeekHigh": stock_info.get("fiftyTwoWeekHigh", None),
        "fiftyTwoWeekLow": stock_info.get("fiftyTwoWeekLow", None),
        "marketCap": stock_info.get("marketCap", None),
        "peRatio": stock_info.get("trailingPE", None),
        "eps": stock_info.get("trailingEps", None),
        "historicalData": hist_data.to_dict(orient="index")  # Convert historical data to dict
    }

    return stock_data
