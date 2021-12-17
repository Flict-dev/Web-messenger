from pydantic import BaseModel


class Room(BaseModel):
    name: str
    password: str


class UserAuth(BaseModel):
    id: int
    accessToken: dict
