from fastapi import FastAPI, Request
import motor.motor_asyncio
import pydantic
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from geopy.geocoders import Nominatim
import  datetime 
from datetime import timedelta
import time

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
now_time = datetime.datetime.now().time()

sunset_time = datetime.datetime.strptime(sunset_api_data['results']['sunset'], '%I:%M:%S %p').time()
utc_time = datetime.time(5, 0, 0)

date = datetime.date(1, 1, 1)
datetime1 = datetime.datetime.combine(date, sunset_time)
datetime2 = datetime.datetime.combine(date, utc_time)
final_sunset_time = str(datetime1 - datetime2)

@app.get("/")
async def home():
    return {"LAB 6": "redirect to /api/state"}


@app.put("/api/state")
async def toggle(request: Request): 
  state = await request.json()
  state["sunset"] = final_sunset_time
  state["now"] = str(now_time)
  state["Time Later than Sunset"] = (now_time>sunset_time)
  obj = await states.find_one({"tobe":"updated"})
  
  if obj:
    await states.update_one({"tobe":"updated"}, {"$set": state})
  else:
    await states.insert_one({**state, "tobe": "updated"})
  new_obj = await states.find_one({"tobe":"updated"}) 
  return new_obj



@app.get("/api/state")
async def get_state():
  state = await states.find_one({"tobe": "updated"})
  
  if state == None:
    return {"temperature": False, "sunset": False}
  return state