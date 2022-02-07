from typing import List
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from db.init_tables import Rooms, Users, Messages, MsgKeys
from fastapi import HTTPException, status
from utils.crypt import Decoder
from core.config import settings


class CoreDatabase:
    def __init__(self, echo: bool = False) -> None:
        self._engine = create_engine(settings.DBURL, echo=echo)
        self._metadata = MetaData()
        self._metadata.reflect(self._engine)
        self._session = sessionmaker(bind=self._engine)
        self._decoder = Decoder(settings.SECRET_KEY)

    @property
    def tables(self) -> List[Table]:
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


class DatabaseRead(CoreDatabase):
    def __init__(self) -> None:
        super().__init__()

    def get_room_by_id(self, id: int) -> Rooms or HTTPException:
        roomTable = self.get_table("Rooms")
        with self.session as session:
            room = session.query(roomTable).where(roomTable.id == id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        return room

    def get_room_by_name(self, name: str) -> Rooms or HTTPException:
        roomTable = self.get_table("Rooms")
        with self.session as session:
            room = session.query(roomTable).where(roomTable.name == name).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        return room

    def get_user_by_id(self, id: int) -> Users or HTTPException:
        usersTable = self.get_table("Users")
        with self.session as session:
            user = session.query(usersTable).where(usersTable.id == id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def get_user_by_name(self, username: str, room_id: int) -> Users or HTTPException:
        room = self.get_room_by_id(room_id)
        names = list(map(lambda x: x.name, room.users))
        try:
            return room.users[names.index(username)]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    def get_all_messages(self, room: Rooms) -> List[Messages]:
        users, messages = room.users, []
        for user in users:
            messages.extend(user.messages)
        return sorted(messages, key=lambda msg: msg.created_at)


class DatabaseCreate(CoreDatabase):
    def __init__(self) -> None:
        super().__init__()

    def create_room(self, name: str, password: str) -> Rooms or HTTPException:
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

    def create_user(self, name: str, admin: bool, room: Rooms) -> Users:
        userTable = self.get_table("Users")
        with self.session as session:
            user = userTable(name=name, admin=admin, room_id=room.id)
            session.expire_on_commit = False
            session.add(user)
            session.commit()
            return user

    def create_message(self, message, user: Users) -> Messages:
        messagesTable = self.get_table("Messages")
        with self.session as session:
            session.expire_on_commit = False
            message = messagesTable(data=message, user_id=user.id, user_name=user.name)
            session.add(message)
            session.commit()
            return message


class DatabaseUpdate(CoreDatabase):
    def __init__(self) -> None:
        super().__init__()

    def ban_user(self, user: Users) -> None:
        with self.session as session:
            user.status = False
            session.add(user)
            session.commit()


class DatabaseDelete(CoreDatabase):
    def __init__(self) -> None:
        super().__init__()

    def delete_room(self, room: Rooms) -> None:
        with self.session as session:
            session.delete(room)
            session.commit()


class Database(DatabaseCreate, DatabaseUpdate, DatabaseDelete, DatabaseRead):
    pass
