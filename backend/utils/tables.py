from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
    PrimaryKeyConstraint,
    DateTime,
    ForeignKey
)


Base = declarative_base()


class Messagees(Base):
    __tablename__ = 'messagees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String)
    created_at = Column(DateTime(), default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.id'))

    __table_args__ = (
        PrimaryKeyConstraint('id', name='message_pk'),
    )


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True)
    name = Column(String(100))
    admin = Column(Boolean)
    messages = relationship(Messagees)
    room_id = Column(Integer, ForeignKey('rooms.id'))

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
    )


class Rooms(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, autoincrement=True)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    users = relationship(Users, back_populates='rooms')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='room_pk'),
        UniqueConstraint('name')
    )


if __name__ == '__main__':
    import os
    db_path = input("Enter db path: ")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    log_path = os.path.abspath(f"../{db_path}")
    print(f"Tables have been created at {log_path}")
