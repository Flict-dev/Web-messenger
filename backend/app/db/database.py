from typing import Dict
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from db.create_tables import Rooms, Users, Messages, MsgKeys
from fastapi import HTTPException, status
from utils.crypt import Decoder
from core.config import settings


class DtabaseHelper:
    def __init__(self, path: str, echo: bool = False) -> None:
        self._engine = create_engine(path, echo=echo)
        self._metadata = MetaData()
        self._metadata.reflect(self._engine)
        self._session = sessionmaker(bind=self._engine)
        self._decoder = Decoder(settings.SECRET_KEY)

    @property
    def tables(self) -> list:
        return list(self._metadata.tables.keys())

    @property
    def session(self) -> Session:
        return self._session()

    def get_table(self, tableName: str) -> Table:
        tables = {
            "Rooms": Rooms,
            "Users": Users,
            "Messages": Messages,
            "MsgKeys": MsgKeys,
        }
        return tables[tableName]

    def check_user(self, username: str, room_id: int) -> bool:
        usersTable = self.get_table("Users")
        with self.session as session:
            user = (
                session.query(usersTable)
                .where(usersTable.name == username, usersTable.room_id == room_id)
                .all()
            )
            return len(user) > 0

    def check_msg_key(self, username: int):
        keyTable = self.get_table("MsgKeys")
        with self.session as session:
            key = (
                session.query(keyTable).where(keyTable.destinied_for == username).all()
            )
            return len(key) > 0


class DatabaseGet(DtabaseHelper):
    def __init__(self, path: str, echo: bool = False) -> None:
        super().__init__(path, echo)

    def get_room_by_id(self, id: int) -> list:
        roomTable = self.get_table("Rooms")
        with self.session as session:
            room = session.query(roomTable).where(roomTable.id == id).first()
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
                )
            return room

    def get_room_by_name(self, name: str) -> list:
        roomTable = self.get_table("Rooms")
        with self.session as session:
            room = session.query(roomTable).where(roomTable.name == name).first()
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
                )
            return room

    def get_user_by_id(self, id: int) -> Users:
        usersTable = self.get_table("Users")
        with self.session as session:
            user = session.query(usersTable).where(usersTable.id == id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user

    def get_user_by_name(self, username: str, room_id: int) -> Users:
        room = self.get_room_by_id(room_id)
        names = list(map(lambda x: x.name, room.users))
        try:
            ind = names.index(username)
            return room.users[ind]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    def get_room_users(self, room_id: int) -> list:
        room = self.get_room_by_id(room_id)
        return room.users

    def get_msg_key(self, room_id: int, destinied_for: str) -> MsgKeys:
        keyTable = self.get_table("MsgKeys")
        with self.session as session:
            key = (
                session.query(keyTable)
                .where(
                    keyTable.room_id == room_id
                    and keyTable.destinied_for == destinied_for
                )
                .first()
            )
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
                )
            return key

    def get_all_messages(self, room_id: int):
        users = self.get_room_users(room_id)
        messages = []
        for user in users:
            for msg in user.messages:
                messages.append(msg)
        messages.sort(key=lambda msg: msg.created_at)
        return messages


class Database(DatabaseGet):
    def __init__(self, path: str, echo: bool = False) -> None:
        super().__init__(path, echo)

    def create_room(self, data: Dict) -> bool:
        roomTable = self.get_table("Rooms")
        try:
            with self.session as session:
                room = roomTable(name=data["name"], password=data["password"])
                session.add(room)
                session.commit()
                self.create_user(
                    {"name": "Admin", "admin": True, "room_id": room.id}, room.id
                )
                return True
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Room name not unique"
            )

    def create_user(self, data: Dict, room_id: int) -> bool:
        userTable = self.get_table("Users")
        try:
            with self.session as session:
                user = userTable(
                    name=data["name"], admin=data["admin"], room_id=data["room_id"]
                )
                session.add(user)
                room = self.get_room_by_id(room_id)
                room.users.append(user)
                session.commit()
            return True
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User name not unique"
            )

    def create_message(self, message, user_id: int) -> bool:
        messagesTable = self.get_table("Messages")
        user = self.get_user_by_id(user_id)
        with self.session as session:
            message = messagesTable(data=message, user_id=user_id)
            session.add(message)
            user.messages.append(message)
            session.commit()

    def create_msg_key(self, room_id: int, destinied_for: str, key: str) -> bool:
        keyTable = self.get_table("MsgKeys")
        if not self.check_msg_key(destinied_for):
            with self.session as session:
                note = keyTable(room_id=room_id, destinied_for=destinied_for, key=key)
                session.add(note)
                session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Key alredy created"
            )

    def delete_key(self, keyId: int):
        keyTable = self.get_table("MsgKeys")
        with self.session as session:
            key = session.query(keyTable).where(keyTable.id == keyId).one()
            session.delete(key)
            session.commit()

    def delete_room(self, room_id: int):
        with self.session as session:
            room = self.get_room_by_id(room_id)
            session.delete(room)
            session.commit()

    def block_user(self, username: str, room_id: int):
        with self.session as session:
            user = self.get_user_by_name(username, room_id)
            user.status = False
            session.add(user)
            session.commit()
