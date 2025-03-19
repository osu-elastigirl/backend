import income_statement
import balance_sheet
import cash_flow_statement
import stock_price
import yfinance as yf
import json
na = "N/A"

def price_earnings(ticker):
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
  try:
    total_assets = balance_sheet.fetch_quarterly(ticker, "Total Assets")
    total_liabilties = balance_sheet.fetch_quarterly(ticker, "Total Liabilities Net Minority Interest")
    te = total_assets - total_liabilties
    return f"{te:.2f}"
  except Exception as e:
    return na

def debt_equity(ticker):
  try:
    total_debt = balance_sheet.fetch_quarterly(ticker, "Total Debt")
    de = total_debt / float(total_equity(ticker))
    return f"{de:.2f}"
  except Exception as e:
    return na

def free_cash_flow(ticker):

  try:
    fcf = cash_flow_statement.fetch_quarterly_TTM(ticker, "Free Cash Flow")
    return f"{fcf:.2f}"
  except Exception as e:
    return na

def free_cash_flow_per_share(ticker):

  try:
    fcf = float(free_cash_flow(ticker))
    out_shares = income_statement.fetch_quarterly_AVG(ticker, "Diluted Average Shares")
    return f"{fcf/out_shares:.2f}"
  except Exception as e:
    return na

"""
def revenue_growth(ticker):
def pe_growth(ticker):

def return_on_investment(ticker):

def return_one_equity(ticker):

def dividend_yeild(ticker):

def beta(ticker):

#net current asset value per share
def ncavps(ticker)

def generate_report(ticker):
"""

def generate_report(ticker):

  data = {
    "price_earnings": price_earnings(ticker),
    "price_book": price_book(ticker),
    "total_equity": total_equity(ticker),
    "debt_equity": debt_equity(ticker),
    "free_cash_flow": free_cash_flow(ticker),
    "free_cash_flow_per_share": free_cash_flow_per_share(ticker),
  }

  return data



