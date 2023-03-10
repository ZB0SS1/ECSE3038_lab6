import os
from fastapi import FastAPI, Request, HTTPException
import motor.motor_asyncio
import pydantic
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import datetime


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


sunset_time = str(datetime.datetime.now()) 

@app.put("/api/state")
async def toggle(request: Request): 
  state = await request.json()

  lights_obj = await states.find_one({"tobe":"updated"})
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
    return {"temperature": 21.0, "sunset": sunset_time}
  return state