import os
import requests

from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Request, Depends
from datetime import datetime 

app = FastAPI()

def get_db_connection():
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.zelara_db
    return db

def get_bearer_token(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Authorization header missing or invalid")
    
    token = authorization.split("Bearer ")[1]
    if not token:
        raise HTTPException(status_code = 401, detail = "Bearer token missing")
    
    return token

@app.get("/")
def read_root():
    return {"message": "Welcome to the Zelara Weather API!"}

@app.get("/api/data")  # appends whatever exists in db-fixtures/fixture.json into the database, returns all entries in the database
def read_data():
    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}))

    if not rows:
        raise HTTPException(status_code = 404, detail = "No data found")

    return {"data": rows}

@app.get("/weather")  # get weather of one specific city
def get_weather_data(city: str, api_key: str = Depends(get_bearer_token)):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code = response.status_code, detail = str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))

def get_geolocation(city: str, api_key: str):
    lat, lon = -1, -1
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        geo_data = response.json()
        if not geo_data:
            raise HTTPException(status_code=404, detail="City not found")
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))

    return (lat, lon)

@app.get("/air_pollution")  # get air quality data of a specific city. latitude and longitude values have to be provided
def get_air_pollution_index(city: str, api_key: str = Depends(get_bearer_token)):
    lat, lon = get_geolocation(city, api_key)
    # Fetch air pollution data
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code = response.status_code, detail = str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/update")  # update a user's location and/or update their weather if more than 24 hours have passed since the last change
def update(_id: int, location: str, api_key: str = Depends(get_bearer_token)):
    db = get_db_connection()
    collection = db["mycollection"]
    current_datetime = datetime.now().strftime('%Y-%m-%d')

    rows = collection.find({"_id": _id})
    for row in rows:
        if location != row["location"] or abs((datetime.strptime(current_datetime, '%Y-%m-%d') - datetime.strptime(row["last_updated"], '%Y-%m-%d'))).days >= 1:
            weather_data = get_weather_data(location, api_key)
            collection.update_one(row, {"$set": {"location": location, "weather_data": weather_data, "last_updated": current_datetime}})
            return {"success": "Updated successfully!"}
        
    return {"data": "0 updates done successfully"}

@app.get("/bulk_refresh")  # bulk refresh everything, egal ob es vor 24 Stunden gemacht wurde oder ned
def bulk_refresh(api_key: str = Depends(get_bearer_token)):
    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}))
    current_datetime = datetime.now().strftime('%Y-%m-%d')
    for row in rows: 
        print(row)
        weather_data = get_weather_data(row["location"], api_key)
        collection.update_one(row, {"$set": {"weather_data": weather_data, "last_updated": current_datetime}})

    rows = list(collection.find({}))

    if not rows:
        raise HTTPException(status_code = 404, detail = "No data found")

    return {"data": rows}