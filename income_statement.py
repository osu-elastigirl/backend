import yfinance as yf
import math
import elastic
na = "N/A"

def get_last_quarterly_report_date(ticker: str):
  stock = yf.Ticker(ticker)
  quarterly_financials = stock.quarterly_financials
  if not quarterly_financials.empty:
    last_report_date = quarterly_financials.columns[0]
    last_report_date = last_report_date.strftime('%Y-%m-%d')
    return last_report_date
  else:
    return None

def fetch_quarterly_TTM(ticker, data_name):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_es = elastic.get_yfinance_metric(ticker, date, data_name)
  if fetch_es == None:  
    company = yf.Ticker(ticker)
    statement = company.quarterly_financials
    value = 0 
    if data_name in statement.index:
      for i in range(4):
        temp = float(statement.loc[data_name][i])
        if math.isnan(temp):
          return "N/A"
        value += temp
      elastic.store_yfinance_metric(ticker, date, data_name, value) 
      return value
  else:  
    return fetch_es
  print(data_name + " does not exists...")
  return "N/A"


def fetch_quarterly_AVG(ticker, data_name):

  date = fundamental_metrics.get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_es = elastic.get_yfinance_metric(ticker, date, data_name)
  if fetch_es == None:  
    company = yf.Ticker(ticker)
    statement = company.quarterly_financials
    value = 0 
    if data_name in statement.index:
      for i in range(4):
        temp = float(statement.loc[data_name][i])
        if math.isnan(temp):
          return "N/A"
        value += temp
      elastic.store_yfinance_metric(ticker, date, data_name, value/4) 
      return value/4
  else:  
    return fetch_es
  print(data_name + " does not exists...")
  return "N/A"

#print(fetch_quarterly_TTM("AAPL", "Total Revenue"))
