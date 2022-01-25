import jwt
from time import time
from core.config import settings
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import status, HTTPException
from jwt.exceptions import DecodeError
from fastapi.encoders import jsonable_encoder as pydantic_decoder


class Encoder:
    def __init__(self, sessionKey: str, sessionAlg: str = "HS256") -> None:
        self._context = CryptContext(schemes=["bcrypt"])
        self._sessionKey = sessionKey
        self.sessionAlg = sessionAlg

    @property
    def key(self):
        key = Fernet.generate_key()
        return str(key, encoding="utf-8")

    @staticmethod
    def gen_hash_link(name: str) -> str:
        return name.split("$")[-1].replace("/", "slash").replace("\\", "hsals")

    def hash_text(self, text: str) -> str:
        return self._context.hash(text)

    def hash_room_data(self, data) -> tuple:
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
        return jwt.encode(
            payload={
                "name": room_name,
                "user_id": user_id,
                "room_id": room_id,
                "admin": admin,
                "msg_key": msg_key,
                "expires": time() + settings.JWT_TIME_LIVE,
            },
            key=self._sessionKey,
            algorithm=self.sessionAlg,
        )


class Decoder:
    def __init__(self, _sessionKey: str, sessionAlg: str = "HS256") -> None:
        self._context = CryptContext(schemes=["bcrypt"])
        self._sessionKey = _sessionKey
        self.sessionAlg = sessionAlg
        self.encoder = Encoder(_sessionKey)

    def decode_session(self, session: str) -> dict:
        try:
            return jwt.decode(session, key=self._sessionKey, algorithms=self.sessionAlg)
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Unauthorized": "Session invalid"},
            )

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return self._context.verify(plain_text, hashed_text)

    def parse_session(self, session):
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

    def session_add_key(self, session: str, msg_key: str) -> str:
        decoded_session = self.decode_session(session)
        return self.encoder.encode_session(
            decoded_session["name"],
            decoded_session["user_id"],
            decoded_session["room_id"],
            decoded_session["admin"],
            msg_key,
        )
