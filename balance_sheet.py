import yfinance as yf
import math

def fetch_quarterly(ticker, data_name):

  company = yf.Ticker(ticker)
  statement = company.quarterly_balance_sheet
  value = None
  if data_name in statement.index:
    value = float(statement.loc[data_name][0])
    if math.isnan(value):
      return "N/A"
    return value
  print(data_name + " does not exists...")
  return "N/A"

