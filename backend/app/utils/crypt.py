from ast import Dict
import jwt
from time import time
from core.config import settings
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import status, HTTPException
from jwt.exceptions import DecodeError
from fastapi.encoders import jsonable_encoder as pydantic_decoder
from passlib.exc import UnknownHashError


class Encoder:
    def __init__(self, sessionKey: str, sessionAlg: str = "HS256") -> None:
        self._context = CryptContext(schemes=["bcrypt"])
        self._sessionKey = sessionKey
        self._sessionAlg = sessionAlg

    @property
    def key(self):
        return str(Fernet.generate_key(), encoding="utf-8")

    @staticmethod
    def gen_hash_link(name: str) -> str:
        return name.split("$")[-1].replace("/", "slash").replace("\\", "hsals")

    def hash_text(self, text: str) -> str or HTTPException:
        try:
            return self._context.hash(text)
        except UnknownHashError:
            raise HTTPException(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"Status", "Invalid hash"},
            )

    def hash_room_data(self, data: Dict) -> tuple or HTTPException:
        json_data = pydantic_decoder(data)
        if json_data["password"] and json_data["name"]:
            return (
                self.hash_text(json_data["name"]),
                self.hash_text(json_data["password"]),
            )
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST, detail={"Invalid room data!"}
        )

    def encode_session(
        self,
        room_name: str,
        user_id: int,
        room_id: int,
        admin: bool,
        msg_key: str,
    ) -> str:
        session = jwt.encode(
            payload={
                "name": room_name,
                "user_id": user_id,
                "room_id": room_id,
                "admin": admin,
                "msg_key": msg_key,
                "expires": time() + settings.JWT_TIME_LIVE,
            },
            key=self._sessionKey,
            algorithm=self._sessionAlg,
        )
        return session


class Decoder:
    def __init__(self, sessionKey: str, sessionAlg: str = "HS256") -> None:
        self._context = CryptContext(schemes=["bcrypt"])
        self._sessionKey = sessionKey
        self._sessionAlg = sessionAlg

    def decode_session(self, session: str) -> dict or HTTPException:
        try:
            return jwt.decode(
                session, key=self._sessionKey, algorithms=self._sessionAlg
            )
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Unauthorized": "Session invalid"},
            )

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return self._context.verify(plain_text, hashed_text)

    def parse_session(self, session: str) -> tuple:
        decoded_session = self.decode_session(session)
        return (
            decoded_session["name"],
            decoded_session["admin"],
            decoded_session["expires"],
        )

    def verify_session(
        self, name: str, session: str, status: bool, admin: bool = False
    ) -> bool:
        s_name, admin, expires = self.parse_session(session)
        verify = s_name == name and status and expires > time()
        return verify and admin if admin else verify

    def get_key(self, session: str) -> str:
        d_session = self.decode_session(session)
        return d_session["msg_key"]
