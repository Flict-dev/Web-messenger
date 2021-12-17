import re
import jwt
from passlib.context import CryptContext


class Validate:
    def __init__(self) -> None:
        self.pattern_password: re = re.compile(
            r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z$%!#^]{8,}$'
        )

    def password(self, password):
        return self.pattern_password.match(password)


class Encoder:
    def __init__(self, sessionKey: str, sessionAlg: str = 'HS256') -> None:
        self.context = CryptContext(schemes=['bcrypt'])
        self.validate = Validate()
        self.sessionKey = sessionKey
        self.sessionAlg = sessionAlg

    def gen_hash_link(self, name) -> str:
        return str(self.context.hash(name))\
            .split('$')[-1]\
            .replace("/", 'slash')\
            .replace("\\", 'slash')

    def hash_password(self, password) -> str:
        if self.validate.password(password):
            return self.context.hash(password)
        raise ValueError("password")

    def create_session(
        self, roomName: str, roomPassword: str, admin: bool
    ) -> str:
        return jwt.encode(
            payload={
                "name": roomName,
                "password": roomPassword,
                "admin": admin
            },
            key=self.sessionKey,
            algorithm=self.sessionAlg
        )
