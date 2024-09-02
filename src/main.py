from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

def get_db_connection():
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.zelara_db
    return db

@app.get("/")
def read_root():
    return {"message": "Welcome to the Zelara Worker API"}

@app.get("/api/data")
def read_data():
    db = get_db_connection()
    collection = db["mycollection"]
    rows = list(collection.find({}, {"_id": 0}))

    if not rows:
        raise HTTPException(status_code=404, detail="No data found")

    return {"data": rows}
