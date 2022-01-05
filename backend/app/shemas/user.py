from pydantic import BaseModel


class UserBlock(BaseModel):
    username: str
