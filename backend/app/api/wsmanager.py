from fastapi import WebSocket
from typing import List
from datetime import datetime

from sqlalchemy.sql.functions import user
from utils.helpers import Parser


class Connection:
    def __init__(self, name: str, websocket: WebSocket) -> None:
        self.name = name
        self.websocket = websocket


class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.connections: List[Connection] = []
        self._parser = Parser()

    def __str__(self):
        return self.name

    async def connect(self, connection: Connection) -> None:
        await connection.websocket.accept()
        await self.send_connections(connection)
        await self.broadcast(201, f"{connection.name} joined chat", connection.name)
        

    async def broadcast(
        self, status: int = 200, message: str = "", username: str = ""
    ) -> None:
        data = {
            "status": status,
            "username": username,
            "message": message,
            "time": self._parser.parse_msg_time(str(datetime.now())),
        }
        for connection in self.connections:
            await connection.websocket.send_json(data)

    async def disconnect(self, connection: Connection):  
        self.connections.remove(connection)


    async def send_connections(self, connection: Connection) -> None:
        named_connections = list(map(lambda x: x.name, self.connections))
        data = {"status": 203, "connections": named_connections}
        await connection.websocket.send_json(data)

    def give_status(self) -> bool:
        return len(self.connections) > 0


class RoomsManager:
    def __init__(self) -> None:
        self.rooms = {}

    def get_room_by_name(self, name: str) -> Room:
        return self.rooms[name]

    def append_room(self, name: str, room: Room) -> None:
        self.rooms[name] = room

    def check_room(self, name: str) -> bool:
        return name in self.rooms.keys()

    def append_room_connection(self, name: str, connection: Connection) -> None:
        room = self.rooms[name]
        room.connections.append(connection)

    async def connect_room(self, name: str, connection:Connection) -> Room:
        room = self.rooms[name]
        await room.connect(connection)
        return room

    def close_room(self, name: str) -> None:
        room = self.rooms[name]
        if not (room.give_status()):
            del self.rooms[name]
