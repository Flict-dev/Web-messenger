from pydantic import BaseModel

class Room(BaseModel):
    name: str
    password: str

class RoomInDb(BaseModel):
    id: int
    hashedPassword: str

class UserAuth(BaseModel):
    id: int
    accessToken: dict
