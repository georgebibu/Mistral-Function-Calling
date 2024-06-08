from fastapi import FastAPI
import requests
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import json
import functools
def books(subject:str):
    url="https://openlibrary.org/subjects/"+subject+".json"
    response=requests.get(url)
    books=json.dumps(response.json())
    return books
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
def addition(a,b):
    s=a+b
    return f"The sum of the numbers using the tool is {s}."
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
    },
    {
        "type": "function",
        "function": {
            "name": "addition",
            "description": "Adds two number and returns a message that says that addition has been achieved using the tool and displays the sum in the message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first operand of the addition operation.",
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second operand of the addition operation.",
                    }
                },
                "required": ["a","b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "books",
            "description": "Returns a list of books and its details that match the subject matter specified in the parameter by making a GET request to openlibrary's API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject matter with which the books are to be searched for in API",
                    }
                },
                "required": ["subject"],
            },
        },
    }
]
names_to_functions = {
    'forecast': functools.partial(forecast),
    'addition': functools.partial(addition),
    'books': functools.partial(books)
}

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/query/")
def weather(query:str):
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    client = MistralClient(api_key=api_key)

    messages=[ChatMessage(role="user", content=query)]
    
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