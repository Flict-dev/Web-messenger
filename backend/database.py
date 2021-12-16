from utils.tables import Users
from sqlalchemy import create_engine, MetaData, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import sessionmaker, Session
URL = 'sqlite:///sqlite.db'


class Database:
    def __init__(self, path: str, echo: bool = False):
        self._engine = create_engine(path, echo=echo)
        self._metadata = MetaData()
        self._metadata.reflect(self._engine)
        self._session = sessionmaker(self._engine)

    @property
    def tables(self):
        return list(self._metadata.tables.keys())

    def create_room(self, data):
      pass