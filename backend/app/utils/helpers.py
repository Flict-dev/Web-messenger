from fastapi.encoders import jsonable_encoder
from datetime import datetime
from db.database import Database
from utils.crypt import Decoder
from core.config import settings
from fastapi import status, HTTPException


class Parser:
    def __init__(self):
        self._database = Database(settings.DBURL)
        self._decoder = Decoder(settings.SECRET_KEY)

    @staticmethod
    def parse_room_data(data) -> tuple:
        json_data = jsonable_encoder(data)
        if json_data["password"] and json_data["name"]:
            return (json_data["name"], json_data["password"])
        raise ValueError("Parse error at room data")

    @staticmethod
    def parse_link_hash(hash: str) -> str:
        return "$2b$12$" + hash.replace("slash", "/").replace("hsals", "\\")

    @staticmethod
    def parse_msg_time(time: str) -> str:
        date = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S.%f")
        return date.strftime("%d-%b %H:%M")

    @staticmethod
    def parse_room_users(users):
        users = list(
            map(
                lambda user: {
                    "name": user.name,
                    "status": user.status,
                    "online": False,
                },
                users,
            )
        )
        return users

    def get_room_data(self, name: str, session: str = "") -> tuple:
        hashed_name = self.parse_link_hash(name)
        room = self._database.get_room_by_name(hashed_name)
        if session:
            user = self._database.get_user_by_name(
                self._decoder.decode_session(session)["username"], room.id
            )
            return (hashed_name, room, user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"Erorr": "Session doesn't exist"},
            headers={"Content-Type": "application/json", "WWW-Authenticate": "Bearer"},
        )
