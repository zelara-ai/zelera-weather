import os
import requests

from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Request, Depends
from datetime import datetime 
from bson import ObjectId

app = FastAPI()
EPS = 1e-4

def get_db_connection():
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.zelara_db
    return db

@app.get("/")
def read_root():
    return {"message": "Welcome to the Zelara Weather API!"}

@app.get("/api/data")  # returns all entries in the database
def read_data():
    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}))

    if not rows:
        raise HTTPException(status_code = 404, detail = "Database is empty")

    for row in rows:
        row["_id"] = str(row["_id"])
    
    return {
        "count": len(rows),
        "data": rows
    }

@app.delete("/")
def delete_all_entries():  # deletes all entries in the database. should NOT be misused.
    db = get_db_connection()
    collection = db["mycollection"]
    result = collection.delete_many({})
    return {
        "status_code": 200,
        "message": f"Deleted {result.deleted_count} documents."
    }

def get_bearer_token(request: Request):  # extracts bearer token from header created whilst making the API call
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Authorization header missing or invalid")
    
    token = authorization.split("Bearer ")[1]
    if not token:
        raise HTTPException(status_code = 401, detail = "Bearer token missing")
    
    return token

def get_response(url):  # a function to handle default behavior when making API calls to openweather
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code = response.status_code, detail = str(http_err))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code = 500, detail = str(e))
    
def get_geolocation(city: str, api_key: str):  # getting latitude and longitude values from a city name 
    lat, lon = -1, -1
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    geo_data = get_response(url)
    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]
    return (lat, lon)

@app.get("/find/city")  # find if a city already exists in the database
def find_city(name: str, lat = None, lon = None, api_key: str = Depends(get_bearer_token)):
    if lat == None and lon == None: 
        lat, lon = get_geolocation(name, api_key)  

    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}))
    for row in rows: 
        geolocation_object = row["weather_data"]["coord"]
        if abs(geolocation_object["lat"] - lat) < EPS and abs(geolocation_object["lon"] - lon) < EPS:
            return {
                "status_code": 200,
                "id": str(row["_id"])
            }
    
    return {
        "status_code": 404,
        "message": "City doesn't exist in the database."
    }

@app.get("/find/id")  # find id of an existing city in the database
def find_id(id: str):
    db = get_db_connection()
    collection = db["mycollection"]
    row = collection.find_one({"_id": ObjectId(id)})
    if row:
        row["_id"] = str(row["_id"])
        return {
            "status_code": 200,
            "data": row
        }

    return {
        "status_code": 404,
        "detail": f"_id {id} does not exist in the database"
    }

@app.post("/add")  # add a new city to the database.  
def add_city(city: str, api_key: str = Depends(get_bearer_token)):
    lat, lon = get_geolocation(city, api_key) 
    if find_city(city, lat, lon)["status_code"] == 200:
            raise HTTPException(status_code = 404, detail = "City already exists in the database.")

    db = get_db_connection()
    collection = db["mycollection"]
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    weather_data = get_response(url)
    data = {
        "weather_data": weather_data,
        "last_updated": datetime.now().strftime("%d.%m.%Y")
    }
    result = collection.insert_one(data)
    return {
        "status_code": "200",
        "message": f"Successfully added object with id {result.inserted_id}"
    }