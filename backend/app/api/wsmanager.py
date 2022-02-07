from fastapi import WebSocket
from typing import List
from datetime import datetime
from utils.helpers import Parser
from abc import ABC, abstractmethod


class Connection:
    """Class for connected user."""

    def __init__(self, name: str, session: str, websocket: WebSocket) -> None:
        self.name = name
        self.websocket = websocket
        self._parser = Parser()
        self.time = self._parser.parse_msg_time(str(datetime.now()))
        self.session = session


class AbstractRoom(ABC):
    """Class for websocket functionality."""

    @property
    @abstractmethod
    def named_connections(self) -> List[dict]:
        """Return a list with all named connections."""

    @abstractmethod
    def connect(self, connection: Connection) -> None:
        """Establishe connection to websocket."""

    @abstractmethod
    async def broadcast(
        self, status: int = 200, message: str = "", username: str = ""
    ) -> None:
        """Send a message to all users."""

    @abstractmethod
    def disconnect(self, connection: Connection) -> None:
        """Kill the connection after the user terminates the connection."""

    @abstractmethod
    def send_connections(self, connection: Connection) -> None:
        """Send all current users online."""

    @abstractmethod
    def send_key(self, connection: Connection, key: str) -> None:
        """Send an encryption key to a specific user."""

    @abstractmethod
    def ban_user(self, connection: Connection, message: str) -> None:
        """Send a message to all users that the user has been banned and also sends it to him."""

    @abstractmethod
    def give_status(self) -> bool:
        """Check if there are connections to the room."""

    @abstractmethod
    def get_connection(self, username: str) -> Connection:
        """Find the connection."""


class Room(AbstractRoom):
    def __init__(self, name: str) -> None:
        self.name = name
        self.connections: List[Connection] = []
        self._parser: Parser = Parser()

    def __str__(self):
        return self.name

    @property
    def named_connections(self) -> List[dict]:
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
            await connection.websocket.send_json(
                {
                    "status": status,
                    "username": username,
                    "message": message,
                    "time": self._parser.parse_msg_time(str(datetime.now())),
                }
            )

    async def disconnect(self, connection: Connection) -> None:
        self.connections.remove(connection)

    async def send_connections(self, connection: Connection) -> None:
        data = {"status": 203, "connections": self.named_connections}
        await connection.websocket.send_json(data)

    async def send_key(self, connection: Connection, key: str) -> None:
        await connection.websocket.send_json(
            {
                "status": 206,
                "username": connection.name,
                "message": key,
                "time": self._parser.parse_msg_time(str(datetime.now())),
            }
        )

    async def ban_user(self, connection: Connection, message: str) -> None:
        await connection.websocket.send_json(
            {
                "status": 207,
                "username": connection.name,
                "message": message,
                "time": self._parser.parse_msg_time(str(datetime.now())),
            }
        )
        await self.broadcast(208, message, connection.name)

    def give_status(self) -> bool:
        return len(self.connections) > 0

    def get_connection(self, username: str) -> Connection:
        for connection in self.connections:
            if connection.name == username:
                return connection


class AbstractRoomsManager(ABC):
    """Class for "manager" functionality."""

    @abstractmethod
    def append_room(self, name: str, room: Room) -> None:
        """Create a new Room object if there isn't done already."""

    @abstractmethod
    def append_room_connection(self, name: str, connection: Connection) -> None:
        """Create a new connection if there is no such connection yet."""

    @abstractmethod
    async def connect_room(self, name: str, connection: Connection) -> Room:
        """Connects to the room."""

    @abstractmethod
    def close_room(self, name: str) -> None:
        """Destroys the Room object if the user is not online."""

    @abstractmethod
    def delete_connections(self, name: str) -> None:
        """Clears all connections in the room."""


class RoomsManager(AbstractRoomsManager):
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
