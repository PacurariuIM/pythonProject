from fastapi import FastAPI
import requests

app = FastAPI(
    title="My nutrition app",
    description="Here we'll help you cut those extra calories!",
    version="1.0.0"
)

url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

menu = input("What have you eaten today?")
querystring = {"query": menu}

headers = {
    "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com",
    "X-RapidAPI-Key": "01ddd026b8mshec61cafc6a64887p1fb588jsndace5b8828ab"
}

response = requests.request("GET", url, headers=headers, params=querystring)
json_response = response.json()
print(json_response)
repo = json_response["items"][0:]
print(repo)
a_key = "calories"
value_of_keys = [a_dict[a_key] for a_dict in repo]
print(sum(value_of_keys))
# calories = repo[8]
# print(calories)
# print(response.text)