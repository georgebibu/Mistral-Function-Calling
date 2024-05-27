from fastapi import FastAPI
import requests
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import json
import functools
def forecast(location):
    KEY: str = "9f52e8256fd0470ea61153159242405"
    url="http://api.weatherapi.com/v1/current.json"
    params={
        "q":location,
        "key":KEY
    }
    response=requests.post(url,params=params)
    forecast=json.dumps(response.json())
    return forecast
tools = [
    {
        "type": "function",
        "function": {
            "name": "forecast",
            "description": "Return a string containing the details of the weather of an area using a POST request to a weather site API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location whose weather is to be determined.",
                    }
                },
                "required": ["location"],
            },
        },
    }
]
names_to_functions = {
    'forecast': functools.partial(forecast),
}

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None,s:str="Bobu"):
    return {"item_id": item_id, "q": q, "s":s}

@app.get("/weather/")
def weather():
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    client = MistralClient(api_key=api_key)

    messages=[ChatMessage(role="user", content=f"What is the weather like in Delhi, India?")]
    
    response = client.chat(model=model, messages=messages, tools=tools, tool_choice="auto")
    messages.append(response.choices[0].message)

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    function_result = names_to_functions[function_name](**function_params)
    print(function_result)
    messages.append(ChatMessage(role="tool", name=function_name, content=function_result, tool_call_id=tool_call.id))

    response = client.chat(model=model, messages=messages)
    return response.choices[0].message.content