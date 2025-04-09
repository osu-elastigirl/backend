import requests
import json
import datetime
from config import FINNHUB_API_KEY  # Your API key should be stored securely here.
import pandas as pd
import httpx

async def get_recommendation_trends(symbol: str) -> list:
    """
    Fetch the latest recommendation trends for the given stock symbol.
    """
    base_url = "https://finnhub.io/api/v1"
    endpoint = "stock/recommendation"
    url = f"{base_url}/stock/recommendation"
    params = {"symbol": symbol, "token": FINNHUB_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_company_news(symbol: str, from_date: str, to_date: str) -> dict:
    """
    Fetch the latest company news for the given stock symbol between from_date and to_date.
    This endpoint is only available for North American companies.
    """
    base_url = "https://finnhub.io/api/v1"
    endpoint = "company-news"
    url = f"{base_url}/company-news"
    params = {"symbol": symbol, "from": from_date, "to": to_date, "token": FINNHUB_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        resp_df = pd.DataFrame(response.json())
        return resp_df[['headline', 'summary', 'url']].to_dict()