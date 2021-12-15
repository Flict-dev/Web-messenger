from pydantic import BaseModel

class Room(BaseModel):
    name: str
    password: str