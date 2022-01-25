from pydantic import BaseModel


class RoomReq(BaseModel):
    name: str
    password: str


class RoomAuth(BaseModel):
    username: str
    password: str
