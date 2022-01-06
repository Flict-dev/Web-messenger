from fastapi.encoders import jsonable_encoder
from datetime import datetime


class Parser:
    def parse_room_data(self, data) -> tuple:
        json_data = jsonable_encoder(data)
        if json_data["password"] and json_data["name"]:
            return (json_data["name"], json_data["password"])
        raise ValueError("Parse error at room data")

    def parse_link_hash(self, hash: str) -> str:
        return "$2b$12$" + hash.replace("slash", "/").replace("hsals", "\\")

    def parse_msg_time(self, time: str) -> str:
        date = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        return date.strftime("%d-%b %Y %H:%M")
