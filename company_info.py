import yfinance as yf 
import json

def fetch_company_info(ticker):
  company = yf.Ticker(ticker)
  information = company.info

  data = {
    "name": information.get("longName", "N/A"), 
    "description": information.get("longBusinessSummary", "N/A"),
    "sector": information.get("sector", "N/A"),
    "industry": information.get("industry", "N/A"),
    "location": information.get("city", "N/A"),
    "country": information.get("country", "N/A"),
    "founded_year": information.get("yearFounded", "N/A"),
    "website": information.get("website", "N/A"),
  } 
  json_struct = {
    ticker: {
      "basic_company_info": data 
    }
  }
  output = json.dumps(json_struct, indent=4)

  with open(f"{ticker}_company_info.json", "w") as json_file:
        json_file.write(output)

  print(f"JSON file for {ticker} has been created successfully!")

fetch_company_info("AAPL")
