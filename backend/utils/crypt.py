import re
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet


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

    @property
    def key(self):
        key = Fernet.generate_key()
        print(key)
        return str(key, encoding='utf-8')

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

    def encode_session(self, roomName: str, roomPassword: str, username: str, msg_key: str) -> str:
        return jwt.encode(
            payload={
                "name": roomName,
                "password": roomPassword,
                "username": username,
                "msg_key": msg_key
            },
            key=self.sessionKey,
            algorithm=self.sessionAlg
        )

    def encrypt_message(self, message: str, msg_key: str) -> str:
        encoded_msg = message.encode()
        fernet = Fernet(msg_key)
        return fernet.encrypt(encoded_msg)


class Decoder:
    def __init__(self, sessionKey: str, sessionAlg: str = 'HS256') -> None:
        self.context = CryptContext(schemes=['bcrypt'])
        self.sessionKey = sessionKey
        self.sessionAlg = sessionAlg
        self.encoder = Encoder(sessionKey)

    def decode_session(self, session: str) -> dict:
        return dict(jwt.decode(session, key=self.sessionKey, algorithms=self.sessionAlg))

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)

    def verify_name(self, name: str, hashed_name: str) -> bool:
        return self.context.verify(name, hashed_name)

    def verify_session(self, name: str, password: str, session: str, admin: bool = False) -> bool:
        decoded_session = self.decode_session(session)
        room_name, room_password = decoded_session['name'], decoded_session['password']
        if admin:
            return (
                room_name == name and self.verify_password(
                    room_password, password
                ) and int(decoded_session['admin'])
            )
        return (
            room_name == name and self.verify_password(
                room_password, password
            )
        )

    def session_add_key(self, session: str, msg_key: str) -> str:
        decoded_session = self.decode_session(session)
        return self.encoder.encode_session(
            decoded_session['name'], 
            decoded_session['password'],
            decoded_session['username'],
            msg_key
        )

    def dcrypt_message(self, encoded_msg: str, msg_key: str) -> str:
        fernet = Fernet(msg_key)
        return fernet.decrypt(encoded_msg)
