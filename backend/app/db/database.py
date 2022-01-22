from typing import Dict
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from db.create_tables import Rooms, Users, Messages, MsgKeys
from fastapi import HTTPException, status
from utils.crypt import Decoder
from core.config import settings
from fastapi.responses import JSONResponse


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

    def check_user(self, username: str, room_id: int):
        usersTable = self.get_table("Users")
        with self.session as session:
            user = (
                session.query(usersTable)
                .where(usersTable.name == username, usersTable.room_id == room_id)
                .all()
            )
        if len(user) > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Erorr": "Username not unique"},
                headers={
                    "Content-Type": "application/json",
                },
            )
        return True


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

    def get_room_users(self, room_id: int) -> list:
        room = self.get_room_by_id(room_id)
        return room.users

    """ May be broken """

    def get_all_messages(self, room_id: int):
        users, messages = self.get_room_users(room_id), []
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
                room = roomTable(name=name, password=password)
                session.add(room)
                session.commit()
                self.create_user("Admin", True, room.id)
                return True
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Room name not unique"
            )

    def create_user(self, name: str, admin: bool, room_id: int) -> bool:
        userTable = self.get_table("Users")
        try:
            with self.session as session:
                user = userTable(name=name, admin=admin, room_id=room_id)
                session.add(user)
                room = self.get_room_by_id(room_id)
                room.users.append(user)
                session.commit()
            return True
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User name not unique"
            )

    def create_message(self, message, user_id: int, user_name: str) -> bool:
        messagesTable = self.get_table("Messages")
        user = self.get_user_by_id(user_id)
        with self.session as session:
            message = messagesTable(data=message, user_id=user_id, user_name=user_name)
            session.add(message)
            user.messages.append(message)
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
