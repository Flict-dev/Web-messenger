from pydantic import BaseModel
from datetime import datetime

class Room(BaseModel):
    id: int
    name: str
    password: str
    admin: str

class User(BaseModel):
  id: int
  name: str
  ip: str
  messages: list
  admin: bool
  

class Message(BaseModel):
  id: int
  data: str
  created_at: datetime
