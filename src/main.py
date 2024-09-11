from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import requests

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise HTTPException(status_code=500, detail="API key not found")

def get_db_connection():
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.zelara_db
    return db

@app.get("/")
def read_root():
    return {"message": "Welcome to the Zelara Weather API!"}

@app.get("/api/data")
def read_data():
    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}, {"_id": 0}))

    if not rows:
        raise HTTPException(status_code=404, detail="No data found")

    return {"data": rows}

@app.get("/weather")
def get_city_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching weather data")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))
    
@app.get("/air_pollution")
def get_air_polution_index(city: str):
    lat, lon = -1, -1
    # fetch latitude and longitude using Geocoding API
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            lat = response.json()[0]["lat"]
            lon = response.json()[0]["lon"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))
    
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching air pollution data")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))