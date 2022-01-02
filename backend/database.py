from typing import Dict
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from utils.tables import Rooms, Users, Messages, MsgKeys
from utils.crypt import Decoder
from main import SECRET_KEY


class DtabaseHelper:
    def __init__(self, path: str, echo: bool = False) -> None:
        self._engine = create_engine(path, echo=echo)
        self._metadata = MetaData()
        self._metadata.reflect(self._engine)
        self._session = sessionmaker(bind=self._engine)
        self._decoder = Decoder(SECRET_KEY)

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

    def check_user(self, username: str, room_id: int) -> bool:
        usersTable = self.get_table('Users')
        with self.session as session:
            user = session.query(usersTable).where(
                usersTable.name == username and usersTable.room_id == room_id
            ).all()
            return len(user) > 0

    def check_msg_key(self, username: int):
        keyTable = self.get_table('MsgKeys')
        with self.session as session:
            key = session.query(keyTable).where(
                keyTable.destinied_for == username).all()
            return len(key) > 1


class DatabaseGet(DtabaseHelper):
    def __init__(self, path: str, echo: bool = False) -> None:
        super().__init__(path, echo)

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

    def get_user_by_name(self, username: str, room_id: int) -> Users:
        room = self.get_room_by_id(room_id)
        for user in room.users:
            if self._decoder.verify_name(username, user.name):
                return user
        raise ValueError("User doesn't exist")

    def get_room_users(self, room_id: int) -> list:
        room = self.get_room_by_id(room_id)
        return room.users

    def get_msg_key(self, room_id: int, destinied_for: str) -> MsgKeys:
        keyTable = self.get_table('MsgKeys')
        try:
            with self.session as session:
                key = session.query(keyTable).where(
                    keyTable.room_id == room_id and keyTable.destinied_for == destinied_for
                ).all()
                return key[0]
        except IndexError:
            raise ValueError("Key doesn't exist")

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

    def create_msg_key(self, room_id: int, destinied_for: str, key: str) -> bool:
        keyTable = self.get_table('MsgKeys')
        if not self.check_msg_key(destinied_for):
            with self.session as session:
                note = keyTable(
                    room_id=room_id, destinied_for=destinied_for, key=key
                )
                session.add(note)
                session.commit()
        raise ValueError('Note already exists')

    def delete_key(self, keyId: int):
        keyTable = self.get_table('MsgKeys')
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


d = Database('sqlite:///sqlite.db')
d.get_all_messages(1)
