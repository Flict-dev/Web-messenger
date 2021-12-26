from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    PrimaryKeyConstraint,
    DateTime,
    ForeignKey
)


Base = declarative_base()


class Messages(Base):
    __tablename__ = 'Messagees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String)
    created_at = Column(DateTime(), default=datetime.now)
    user_id = Column(Integer, ForeignKey('Users.id'))

    __table_args__ = (
        PrimaryKeyConstraint('id', name='message_pk'),
    )


class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, autoincrement=True)
    name = Column(String(100))
    admin = Column(Boolean)
    messages = relationship("Messages", lazy='subquery', cascade="all, delete, delete-orphan",)
    room_id = Column(Integer, ForeignKey('Rooms.id'))
    room = relationship("Rooms", back_populates="users")
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
    )


class Rooms(Base):
    __tablename__ = 'Rooms'

    id = Column(Integer, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    users = relationship("Users", cascade="all, delete, delete-orphan", back_populates='room', lazy='subquery')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='room_pk'),
    )


if __name__ == '__main__':
    import os
    db_path = input("Enter db path: ")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    log_path = os.path.abspath(f"../{db_path}")
    print(f"Tables have been created at {log_path}")
