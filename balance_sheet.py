import yfinance as yf
import math
import elastic


def get_last_quarterly_report_date(ticker: str):
  stock = yf.Ticker(ticker)
  quarterly_financials = stock.quarterly_financials
  if not quarterly_financials.empty:
    last_report_date = quarterly_financials.columns[0]
    last_report_date = last_report_date.strftime('%Y-%m-%d')
    return last_report_date
  else:
    return None

def fetch_quarterly(ticker, data_name):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_es = elastic.get_yfinance_metric(ticker, date, data_name)
  if fetch_es == None:  
    company = yf.Ticker(ticker)
    statement = company.quarterly_balance_sheet
    value = None
    if data_name in statement.index:
      value = float(statement.loc[data_name][0])
      if math.isnan(value):
        return "N/A"
      elastic.store_yfinance_metric(ticker, date, data_name, value)
      return value
  else:  
    return fetch_es
  print(data_name + " does not exists...")
  return "N/A"

