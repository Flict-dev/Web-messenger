from pydantic import BaseModel


class RoomReq(BaseModel):
    name: str
    password: str


class RoomAuth(BaseModel):
    username: str
    password: str


class UserAuth(BaseModel):
    id: int
    accessToken: dict
