from re import I
from tkinter import N
from fastapi import WebSocket
from typing import List
from datetime import datetime

from sqlalchemy.sql.functions import user
from utils.helpers import Parser


class Connection:
    def __init__(self, name: str, session: str, websocket: WebSocket) -> None:
        self.name = name
        self.websocket = websocket
        self._parser = Parser()
        self.time = self._parser.parse_msg_time(str(datetime.now()))
        self.session = session


class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.connections: List[Connection] = []
        self._parser = Parser()

    def __str__(self):
        return self.name

    @property
    def named_connections(self) -> List:
        return list(map(lambda x: {"name": x.name, "time": x.time}, self.connections))

    async def connect(self, connection: Connection) -> None:
        await connection.websocket.accept()
        connection.time = self._parser.parse_msg_time(str(datetime.now()))
        await self.send_connections(connection)
        await self.broadcast(201, f"{connection.name} joined chat", connection.name)

    async def broadcast(
        self, status: int = 200, message: str = "", username: str = ""
    ) -> None:
        for connection in self.connections:
            await connection.websocket.send_json({
                "status": status,
                "username": username,
                "message": message,
                "time": self._parser.parse_msg_time(str(datetime.now())),
            })

    async def disconnect(self, connection: Connection) -> None:
        self.connections.remove(connection)

    async def send_connections(self, connection: Connection) -> None:
        data = {"status": 203, "connections": self.named_connections}
        await connection.websocket.send_json(data)

    async def send_key(self, connection, key) -> None:
        await connection.websocket.send_json({
            "status": 206,
            "username": connection.name,
            "message": key,
            "time": self._parser.parse_msg_time(str(datetime.now())),
        })
            

    async def ban_user(self, connection: Connection, message: str) -> None:
        await connection.websocket.send_json({
            "status": 207,
            "username": connection.name,
            "message": message,
            "time": self._parser.parse_msg_time(str(datetime.now())),
        })
        await self.broadcast(208, message, connection.name)

    def give_status(self) -> bool:
        return len(self.connections) > 0

    def get_connection(self, username: str) -> Connection:
        for connection in self.connections:
            if connection.name == username:
                return connection


class RoomsManager:
    def __init__(self) -> None:
        self.rooms = {}

    def append_room(self, name: str, room: Room) -> None:
        if name not in self.rooms.keys():
            self.rooms[name] = room

    def append_room_connection(self, name: str, connection: Connection) -> None:
        room = self.rooms[name]
        if connection.name not in list(map(lambda x: x.name, room.connections)):
            room.connections.append(connection)

    async def connect_room(self, name: str, connection: Connection) -> Room:
        room = self.rooms[name]
        await room.connect(connection)
        return room

    def close_room(self, name: str) -> None:
        room = self.rooms[name]
        if not (room.give_status()):
            del self.rooms[name]

    def delete_connections(self, name: str) -> None:
        room = self.rooms[name]
        room.connections = []
