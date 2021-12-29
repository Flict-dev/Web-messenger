from typing import Dict
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from utils.tables import Rooms, Users, Messages, MsgKeys


class Database:
    def __init__(self, path: str, echo: bool = False) -> None:
        self._engine = create_engine(path, echo=echo)
        self._metadata = MetaData()
        self._metadata.reflect(self._engine)
        self._session = sessionmaker(bind=self._engine)

    @property
    def tables(self) -> list:
        return list(self._metadata.tables.keys())

    @property
    def session(self) -> Session:
        return self._session()

    def get_table(self, tableName: str) -> Table:
        tables = {
            'Rooms': Rooms,
            'Users': Users,
            'Messages': Messages,
            'MsgKeys': MsgKeys
        }
        return tables[tableName]

    def get_room_by_id(self, id: int) -> list:
        roomTable = self.get_table('Rooms')
        try:
            with self.session as session:
                room = session.query(roomTable).where(
                    roomTable.id == id
                ).all()
                return room[0]
        except IndexError:
            raise ValueError("Room doesn't exist")

    def get_room_by_name(self, name: str) -> list:
        roomTable = self.get_table('Rooms')
        try:
            with self.session as session:
                room = session.query(roomTable).where(
                    roomTable.name == name
                ).all()
                return room[0]
        except IndexError:
            raise ValueError("Room doesn't exist")

    def get_user_by_id(self, id: int) -> Users:
        usersTable = self.get_table('Users')
        try:
            with self.session as session:
                user = session.query(usersTable).where(
                    usersTable.id == id
                ).all()
                return user[0]
        except IndexError:
            raise ValueError("User doesn't exist")

    def get_user_by_name(self, name: str) -> Users:
        usersTable = self.get_table('Users')
        try:
            with self.session as session:
                user = session.query(usersTable).where(
                    usersTable.name == name
                ).all()
                return user[0]
        except IndexError:
            raise ValueError("User doesn't exist")

    def get_room_users(self, room_id: int) -> list:
        room = self.get_room_by_id(room_id)
        users = []
        for user in room.users:
            users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "admin": user.admin,
                    "messages": user.messages
                }
            )
        return users

    def check_user(self, username: str) -> bool:
        usersTable = self.get_table('Users')
        with self.session as session:
            user = session.query(usersTable).where(
                usersTable.name == username
            ).all()
            return len(user) > 0

    def create_room(self, data: Dict) -> bool:
        roomTable = self.get_table('Rooms')
        try:
            with self.session as session:
                room = roomTable(name=data['name'], password=data['password'])
                session.add(room)
                session.commit()
                self.create_user({
                    'name': 'Admin',
                    'admin': True,
                    'room_id': room.id
                }, room.id)
                return True
        except IntegrityError:
            raise ValueError('roomName')

    def create_user(self, data: Dict, room_id: int) -> bool:
        userTable = self.get_table('Users')
        try:
            with self.session as session:
                user = userTable(
                    name=data['name'], admin=data['admin'], room_id=data['room_id']
                )
                session.add(user)
                room = self.get_room_by_id(room_id)
                room.users.append(user)
                session.commit()
            return True
        except IntegrityError:
            raise ValueError('userName')

    def create_message(self, message, user_id: int) -> bool:
        try:
            messagesTable = self.get_table('Messages')
            user = self.get_user_by_id(user_id)
            with self.session as session:
                message = messagesTable(data=message, user_id=user_id)
                session.add(message)
                user.messages.append(message)
                session.commit()
                return True
        except ValueError:
            return False
