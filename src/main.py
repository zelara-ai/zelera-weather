from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Request, Depends
import os
import requests

app = FastAPI()

def get_db_connection():
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.zelara_db
    return db

def get_bearer_token(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = authorization.split("Bearer ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token missing")
    
    return token

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
def get_city_weather(city: str, api_key: str = Depends(get_bearer_token)):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_geolocation(city: str, api_key: str):
    lat, lon = -1, -1
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        geo_data = response.json()
        if not geo_data:
            raise HTTPException(status_code=404, detail="City not found")
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return (lat, lon)

@app.get("/air_pollution")
def get_air_pollution_index(city: str, api_key: str = Depends(get_bearer_token)):
    lat, lon = get_geolocation(city, api_key)
    # Fetch air pollution data
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
