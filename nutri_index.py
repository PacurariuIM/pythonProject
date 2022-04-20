from fastapi import FastAPI
import requests
import json

app = FastAPI(
    title="My nutrition app",
    description="Here we'll help you cut those extra calories!",
    version="1.0.0"
)

url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

@app.post("/")
def post_menu(menu):
    querystring = {"query": menu}
    headers = {
        "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com",
        "X-RapidAPI-Key": "01ddd026b8mshec61cafc6a64887p1fb588jsndace5b8828ab"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    json_response = response.json()
    repo = json_response["items"][0:]
    a_key = "calories"
    a_value = [a_dict[a_key] for a_dict in repo]
    return sum(a_value)
