from fastapi import FastAPI
import requests
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import json
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None,s:str="Bobu"):
    return {"item_id": item_id, "q": q, "s":s}

@app.get("/weather/")
def weather( query: str = "Delhi India"):
    KEY: str = "9f52e8256fd0470ea61153159242405"
    url="http://api.weatherapi.com/v1/current.json"
    params={
        "q":query,
        "key":KEY
    }
    response=requests.post(url,params=params)
    forecast=json.dumps(response.json())
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    client = MistralClient(api_key=api_key)

    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=f"Please provide a weather update for the given location in a formal, news reporting style. The data is: {forecast}")]
    )
    return chat_response.choices[0].message.content