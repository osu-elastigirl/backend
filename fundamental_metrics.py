import income_statement
import balance_sheet
import cash_flow_statement
import stock_price

na = "N/A"

def price_earnings(ticker):
  try:
    pe = stock_price.fetch(ticker) / income_statement.fetch_quarterly_TTM(ticker, "Diluted EPS")
    return pe
  except Exception as e:
    return na


"""

def price_book(ticker):
def debt_equity(ticker):

def free_cash_flow_per_share(ticker):

def pe_growth(ticker):

def revenue_growth(ticker):

def return_on_investment(ticker):

def return_one_equity(ticker):

def dividend_yeild(ticker):

def beta(ticker):

#net current asset value per share
def ncavps(ticker)

def generate_report(ticker):
"""  
