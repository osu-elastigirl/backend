import json
import datetime
from services.finnhub_service import get_recommendation_trends, get_company_news


def main():
    # List of stocks you want to process.
    stocks = [
        "AAPL",   # Apple Inc.
        "MSFT",   # Microsoft Corporation
        "GOOGL",  # Alphabet Inc.
        "AMZN",   # Amazon.com, Inc.
        "TSLA",   # Tesla, Inc.
        "META",   # Meta Platforms, Inc.
        "NFLX",   # Netflix, Inc.
        "NVDA",   # NVIDIA Corporation
        "BRK.B",  # Berkshire Hathaway Inc. (Class B)
        "JPM",    # JPMorgan Chase & Co.
        "V",      # Visa Inc.
        "UNH",    # UnitedHealth Group Incorporated
        "HD",     # The Home Depot, Inc.
        "PG",     # The Procter & Gamble Company
        "DIS"     # The Walt Disney Company
    ]
    
    # Use today's date for the news; format: YYYY-MM-DD.
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Dictionary to store all data.
    all_stock_data = {}
    
    for stock in stocks:
        print(f"Fetching data for {stock}...")
        
        try:
            rec_trends = get_recommendation_trends(stock)
        except Exception as e:
            print(f"Error fetching recommendation trends for {stock}: {e}")
            rec_trends = []
        
        try:
            news = get_company_news(stock, from_date=today, to_date=today)
        except Exception as e:
            print(f"Error fetching company news for {stock}: {e}")
            news = []
        
        all_stock_data[stock] = {
            "recommendation_trends": rec_trends,
            "company_news": news
        }
    
    # Write the data to a JSON file with pretty printing.
    output_filename = "stocks_data.json"
    with open(output_filename, "w") as f:
        json.dump(all_stock_data, f, indent=2)
    
    print(f"Data has been saved to {output_filename}")

if __name__ == "__main__":
    main()