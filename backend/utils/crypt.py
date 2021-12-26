import re
import jwt
from passlib.context import CryptContext


class Validate:
    def __init__(self) -> None:
        self.pattern_password: re = re.compile(
            r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z$%!#^]{8,}$'
        )

    def password(self, password) -> bool:
        return self.pattern_password.match(password)


class Encoder:
    def __init__(self, sessionKey: str, sessionAlg: str = 'HS256') -> None:
        self.context = CryptContext(schemes=['bcrypt'])
        self.validate = Validate()
        self.sessionKey = sessionKey
        self.sessionAlg = sessionAlg

    def gen_hash_link(self, name: str) -> str:
        return name.split('$')[-1]\
            .replace("/", 'slash')\
            .replace("\\", 'hsals')

    def hash_password(self, password: str) -> str:
        if self.validate.password(password):
            return self.context.hash(password)
        raise ValueError("password")

    def hash_name(self, name: str) -> str:
        if name:
            return self.context.hash(name)
        raise ValueError("name")

    def encode_session(self, roomName: str, roomPassword: str, username: str) -> str:
        return jwt.encode(
            payload={
                "name": roomName,
                "password": roomPassword,
                "username": username
            },
            key=self.sessionKey,
            algorithm=self.sessionAlg
        )


class Decoder:
    def __init__(self, sessionKey: str, sessionAlg: str = 'HS256') -> None:
        self.context = CryptContext(schemes=['bcrypt'])
        self.sessionKey = sessionKey
        self.sessionAlg = sessionAlg

    def decode_session(self, session: str) -> dict:
        return dict(jwt.decode(session, key=self.sessionKey, algorithms=self.sessionAlg))

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)

    def verify_name(self, name: str, hashed_name: str) -> bool:
        return self.context.verify(name, hashed_name)

    def verify_session(self, name: str, password: str, session: str) -> bool:
        decoded_session = self.decode_session(session)
        room_name, room_password = decoded_session['name'], decoded_session['password']
        return (
            room_name == name and self.verify_password(room_password, password)
        )
