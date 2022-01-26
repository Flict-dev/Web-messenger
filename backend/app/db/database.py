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

    @staticmethod
    def get_table(tableName: str) -> Table:
        tables = {
            "Rooms": Rooms,
            "Users": Users,
            "Messages": Messages,
            "MsgKeys": MsgKeys,
        }
        return tables[tableName]


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

    """ May be broken """

    def get_user_by_name(self, username: str, room_id: int) -> Users:
        room = self.get_room_by_id(room_id)
        names = list(map(lambda x: x.name, room.users))
        try:
            return room.users[names.index(username)]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    """ May be broken """

    def get_all_messages(self, room: Rooms):
        users, messages = room.users, []
        for user in users:
            messages.extend(user.messages)
        return sorted(messages, key=lambda msg: msg.created_at)


class Database(DatabaseGet):
    def __init__(self, path: str, echo: bool = False) -> None:
        super().__init__(path, echo)

    def create_room(self, name: str, password: str) -> bool:
        roomTable = self.get_table("Rooms")
        try:
            with self.session as session:
                session.expire_on_commit = False
                room = roomTable(name=name, password=password)
                session.add(room)
                session.commit()
                return room
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Room name not unique"
            )

    def create_user(self, name: str, admin: bool, room: Rooms) -> bool:
        userTable = self.get_table("Users")
        with self.session as session:
            user = userTable(name=name, admin=admin, room_id=room.id)
            session.expire_on_commit = False
            session.add(user)
            session.commit()
            return user

    def create_message(self, message, user: Users) -> bool:
        messagesTable = self.get_table("Messages")
        with self.session as session:
            session.expire_on_commit = False
            message = messagesTable(data=message, user_id=user.id, user_name=user.name)
            session.add(message)
            session.commit()
            return message

    def delete_room(self, room: Rooms):
        with self.session as session:
            session.delete(room)
            session.commit()

    def block_user(self, username: str, room_id: int):
        with self.session as session:
            user = self.get_user_by_name(username, room_id)
            user.status = False
            session.add(user)
            session.commit()
