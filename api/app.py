import os
from fastapi import FastAPI, Request, HTTPException
import motor.motor_asyncio
import pydantic
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from geopy.geocoders import Nominatim
import datetime
import requests


app = FastAPI()

origins = [
    "https://rg-lab6-api.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://IOT_CLASS:iotclass@cluster0.irzkjxq.mongodb.net/?retryWrites=true&w=majority")
db = client.lab_6
states = db["state"]

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str


geolocator = Nominatim(user_agent="MyApp")

location = geolocator.geocode("Hyderabad")

user_latitude =  location.latitude
user_longitude = location.longitude

sunset_api_endpoint = f'https://api.sunrise-sunset.org/json?lat={user_latitude}&lng={user_longitude}'

sunset_api_response = requests.get(sunset_api_endpoint)
sunset_api_data = sunset_api_response.json()

current_date = datetime.date.today()
sunset_time = datetime.datetime.strptime(sunset_api_data['results']['sunset'], '%I:%M:%S %p').time()

now_time = str(datetime.datetime.now())

@app.put("/api/state")
async def toggle(request: Request): 
  state = await request.json()

  lights_obj = await states.find_one({"tobe":"updated"})
  lights_obj["sunset"] = sunset_time
  if lights_obj:
    await states.update_one({"tobe":"updated"}, {"$set": state})

  else:
    await states.insert_one({**state, "tobe": "updated"})
  
  new_ligts_obj = await states.find_one({"tobe":"updated"}) 

  return new_ligts_obj



@app.get("/api/state")
async def get_state():
  state = await states.find_one({"tobe": "updated"})
  
  if state == None:
    return {"temperature": False, "sunset": False}
  return state