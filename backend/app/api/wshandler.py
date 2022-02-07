from core.tools import encoder, decoder, database
from api.wsmanager import Room, Connection
from abc import ABC, abstractmethod
from typing import Dict


class AbstractHandler(ABC):
    """Request handler for websockets."""

    @abstractmethod
    def hadnlers(self, status: int):
        """Set handler."""

    @abstractmethod
    def send_message(self, data: Dict) -> None:
        """Method for sending messages."""

    @abstractmethod
    def send_key(self, data: Dict) -> None:
        """Method for sending encryption key."""

    @abstractmethod
    def ban_user(self, data: Dict) -> None:
        """Method for banning users."""


class WsHandler(AbstractHandler):
    def __init__(self, room: Room, connection: Connection) -> None:
        self._database = database
        self._room = room
        self._decoder = decoder
        self._encoder = encoder
        self._connection = connection

    def hadnlers(self, status: int):
        hadnlers = {200: self.send_message, 206: self.send_key, 207: self.ban_user}
        return hadnlers[status]

    async def send_message(self, data: Dict) -> None:
        user, message = data["user"], data["message"]
        self._database.create_message(message, user)
        await self._room.broadcast(200, message, user.name)

    async def send_key(self, data: Dict) -> None:
        username, message = data["username"], data["message"]
        if data["admin"]:
            connection = self._room.get_connection(username)
            decoded = self._decoder.decode_session(connection.session)
            new_sesion = self._encoder.encode_session(
                decoded["name"], decoded["user_id"], decoded["room_id"], False, message
            )
            await self._room.send_key(connection, new_sesion)

    async def ban_user(self, data: Dict) -> None:
        username, room = data["username"], data["room"]
        if data["admin"]:
            connection = self._room.get_connection(username)
            banned_user = self._database.get_user_by_name(username, room.id)
            self._database.ban_user(banned_user)
            await self._room.ban_user(connection, data["message"])
