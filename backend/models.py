from pydantic import BaseModel


class RoomReq(BaseModel):
    name: str
    password: str


class RoomAuth(BaseModel):
    username: str
    password: str


class MsgKeysCreate(BaseModel):
    destinied_for: str
    key: str


class MsgKeysGet(BaseModel):
    destinied_for: str
