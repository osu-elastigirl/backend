import yfinance as yf
import math

def fetch(ticker):
  stock = yf.Ticker(ticker)
  prices = stock.history(period ="1d")
  if math.isnan(float(prices['Close'][0])):
    return "N/A"  
  return float(prices['Close'][0])

print(fetch("AAPL"))

