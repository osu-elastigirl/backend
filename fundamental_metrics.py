import income_statement
import balance_sheet
from datetime import datetime
import cash_flow_statement
import stock_price
import pandas as pd
import numpy as np
import yfinance as yf
import json
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


def price_earnings(ticker):
  #date = get_date
  #fetch_es = elastic.get_yfinance_metric(ticker, date, "price_earnings")
  try:
    pe = stock_price.fetch(ticker) / income_statement.fetch_quarterly_TTM(ticker, "Diluted EPS")
    return f"{pe:.2f}"
  except Exception as e:
    return na

def price_book(ticker):

  stock = yf.Ticker(ticker)
  stats = stock.info
  return stats.get('priceToBook', 'N/A')
  
def total_equity(ticker):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_es = elastic.get_yfinance_metric(ticker, date, "total_equity")
  if fetch_es == None:
    try:
      total_assets = balance_sheet.fetch_quarterly(ticker, "Total Assets")
      total_liabilties = balance_sheet.fetch_quarterly(ticker, "Total Liabilities Net Minority Interest")
      te = total_assets - total_liabilties
      elastic.store_yfinance_metric(ticker, date, "total_equity", te)
      return f"{te:.2f}"
    except Exception as e:
      return na
  return fetch_es

def debt_equity(ticker):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na

  fetch_de = elastic.get_yfinance_metric(ticker, date, "debt_equity")
  if fetch_de == None:
    try:
      total_debt = balance_sheet.fetch_quarterly(ticker, "Total Debt")
      de = total_debt / float(total_equity(ticker))
      elastic.store_yfinance_metric(ticker, date, "debt_equity", de)
      return f"{de:.2f}"
    except Exception as e:
      return na
  return fetch_de


def free_cash_flow(ticker):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_fcf = elastic.get_yfinance_metric(ticker, date, "free_cash_flow")

  if fetch_fcf == None:
    try:
      fcf = cash_flow_statement.fetch_quarterly_TTM(ticker, "Free Cash Flow")
      elastic.store_yfinance_metric(ticker, date, "free_cash_flow", fcf)
      return f"{fcf:.2f}"
    except Exception as e:
      return na
  return fetch_fcf 

def free_cash_flow_per_share(ticker):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_fcf_ps = elastic.get_yfinance_metric(ticker, date, "free_cash_flow_per_share")
  if fetch_fcf_ps == None: 
    try:
      fcf = float(free_cash_flow(ticker))
      out_shares = income_statement.fetch_quarterly_AVG(ticker, "Diluted Average Shares")
      fcf_ps = fcf/out_shares
      elastic.store_yfinance_metric(ticker, date, "free_cash_flow_per_share", fcf_ps)
      return f"{fcf_ps:.2f}"
    except Exception as e:
      return na
  return fetch_fcf_ps 

# Last 4 years growth
def revenue_growth(ticker):

  date = get_last_quarterly_report_date(ticker)
  if date == None:
    return na
  fetch_rev_gr = elastic.get_yfinance_metric(ticker, date, "revenue_growth")
  print(fetch_rev_gr)
  if fetch_rev_gr == None:

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
      return na   
    ret = avg / 3
    elastic.store_yfinance_metric(ticker, date, "revenue_growth", ret)
    return f"{avg / 3:.2f}%" 
  return fetch_rev_gr


def dividend_yeild(ticker):

  stock = yf.Ticker(ticker)
  dividend_yield = stock.info['dividendYield']
  try:
    return f"{dividend_yield:.2f}%"  
  except Exception as e:
    return na


def beta(ticker):
  try:
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
    return f"{beta_value:.2f}"
  except Exception as e:
    print(e)
    return na

"""
def pe_growth(ticker):

def return_on_investment(ticker):

def return_one_equity(ticker):
#net current asset value per share
def ncavps(ticker)
"""

def generate_report(ticker):

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

  return data

