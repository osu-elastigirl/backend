from google import genai
from pydantic import BaseModel, TypeAdapter

class Ticker(BaseModel):
    symbol: str
    
    def __repr__(self):
        return self.symbol

class Recommendation(BaseModel):
    ticker: str
    rationale: str
    metric_keys: list[str]
    
def getTickers(api_key:str, description:str):
    client = genai.Client(api_key=api_key)
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Give me the tickers for stocks based on this description: ' + description,
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[Ticker],
        },
    )

def get_recommendations(api_key:str, description:str,tickers:list[str], data:dict):
    client = genai.Client(api_key=api_key)
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Here are some stocks that matched the description ' + description + ':' + ', '.join(tickers) + '.' + 'Here is some data we have compiled about them: ' + str(data) + '. Narrow down the number of stocks, provide a rationale based on the data and nature of the company for each stock you recommend, and provide the dict keys for each metric you used to reach this conclusion.',
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[Recommendation],
        },
    )