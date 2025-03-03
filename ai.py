from google import genai
from pydantic import BaseModel, TypeAdapter


class Recommendation(BaseModel):
    ticker: str
    rationale: str

def get_recommendations(description:str, api_key:str):
    client = genai.Client(api_key=api_key)
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Give me recommendations for stocks based on this description: ' + description,
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[Recommendation],
        },
    )