import yfinance as yf
import math
from datetime import datetime
import os

def fetch(ticker):
  stock = yf.Ticker(ticker)
  prices = stock.history(period ="1d")
  if math.isnan(float(prices['Close'].iloc[0])):
    return "N/A"  
  return float(prices['Close'].iloc[0])

def fetch_historical(ticker):
   
  stock = yf.Ticker(ticker)
  today = datetime.now().strftime('%Y-%m-%d')
  stock_data = yf.download(ticker, end=today)

  #currently just going into the below path
  #need this to go to front end?
  csv_file = f"./{ticker}.csv"
  stock_data.to_csv(csv_file)


# uncomment to get max file of stock data, input ticker
#fetch_historical("AAPL")
