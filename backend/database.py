from typing import Dict
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError


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
        return self._metadata.tables[tableName]

    def create_room(self, data: Dict) -> bool:
        roomTable = self.get_table('rooms')
        try:
            with self.session as session:
                session.execute(roomTable.insert().values(**data))
                session.commit()
                roomId = session.query(
                    func.max(roomTable.columns['id'])
                ).all()[0]
                self.create_user({
                    'name': 'Admin',
                    'admin': True,
                    'room_id': roomId
                })
                return True
        except IntegrityError:
            return False

    def create_user(self, data: Dict) -> bool:
        userTable = self.get_table('users')
        try:
            with self.session as session:
                session.execute(userTable.insert().values(**data))
                session.commit()
            return True
        except IntegrityError:
            return False
