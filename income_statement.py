import yfinance as yf
import math

def fetch_quarterly_TTM(ticker, data_name):

  company = yf.Ticker(ticker)
  statement = company.quarterly_financials
  value = 0 
  if data_name in statement.index:
    for i in range(4):
      temp = float(statement.iloc[data_name][i])
      if math.isnan(temp):
        return "N/A"
      value += temp
    return value

  print(data_name + " does not exists...")
  return "N/A"

def fetch_quarterly_AVG(ticker, data_name):

  company = yf.Ticker(ticker)
  statement = company.quarterly_financials
  value = 0 
  if data_name in statement.index:
    for i in range(4):
      temp = float(statement.loc[data_name][i])
      if math.isnan(temp):
        return "N/A"
      value += temp
    return value/4
  print(data_name + " does not exists...")
  return "N/A"


