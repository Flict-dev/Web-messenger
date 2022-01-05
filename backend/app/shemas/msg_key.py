from pydantic import BaseModel


class MsgKeysCreate(BaseModel):
    destinied_for: str
    key: str
