# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
import requests
import json 
# import pandas as pd
from firebase_functions import params
from datetime import datetime

initialize_app()

FINNHUB_API_KEY = params.SecretParam("FINNHUB_API_KEY")

@https_fn.on_request()
def get_recommendation_trends(req: https_fn.Request) -> https_fn.Response:
    symbol = req.args.get("symbol")

    if not symbol: 
        return https_fn.Response(
            json.dumps({"error": "Symbol parameter is required"}),
            status=400,
            content_type="application/json"
        )
    try: 
        base_url = "https://finnhub.io/api/v1"
        endpoint = "stock/recommendation"
        url = f"{base_url}/{endpoint}"
        params = { 
            "symbol": symbol, 
            "token": FINNHUB_API_KEY.value
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()

        return https_fn.Response(
            json.dumps(response.json()),
            content_type="application/json"
        )
    except requests.exceptions.RequestException as e: 
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500, 
            content_type="application/json"
        )

@https_fn.on_request()
def get_company_news(req: https_fn.Request) -> https_fn.Response:
    symbol = req.args.get("symbol")
    from_date = req.args.get("from_date")
    to_date = req.args.get("to_date")
    
    if not all([symbol, from_date, to_date]):
        return https_fn.Response(
            json.dumps({"error": "symbol, from_date, and to_date parameters are required"}),
            status=400,
            content_type="application/json"
        )

    # do we need to validate time stamp??

    try: 
        base_url = "https://finnhub.io/api/v1"
        endpoint = "company-news"
        url = f"{base_url}/{endpoint}"
        params = { 
            "symbol": symbol, 
            "from": from_date,
            "to": to_date,
            "token": FINNHUB_API_KEY.value
        }
        response = requests.get(url, params=params)
        response.raise_for_status()

        try: 
            resp_df = pd.DataFrame(response.json()) # if i get rid of the import pandas up here the pd is no longer defined
            # but if i keep it, then it throws an error when i do firebase deploy --only functions
            if not resp_df.empty: 
                ret = resp_df[['headline', 'summary', 'url']]
                return https_fn.Response(
                    json.dumps(ret.to_dict('records')),
                    content_type="application/json"
                )
            else: 
                return https_fn.Response(
                    json.dumps([]),
                    content_type="application/json"
                )
        except Exception as e: 
            return https_fn.Response(
                json.dumps({"error": f"Failed to process response: {str(e)}"}),
                status = 500, 
                content_type = "application/json"
            )
    except requests.exceptions.RequestException as e: 
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            content_type="application/json"
        )
        