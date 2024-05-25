from fastapi import FastAPI
import requests
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None,s:str="Bobu"):
    return {"item_id": item_id, "q": q, "s":s}

@app.get("/weather/")
def weather( query: str = "Delhi"):
    KEY: str = "9f52e8256fd0470ea61153159242405"
    url="http://api.weatherapi.com/v1/current.json"
    params={
        "q":query,
        "key":KEY
    }
    response=requests.post(url,params=params)
    return response.json()['current']