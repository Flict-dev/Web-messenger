from fastapi import WebSocket
from typing import List


class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.connections: List[WebSocket] = []

    def __str__(self):
        return self.name

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def broadcast(self, message: str) -> None:
        for connection in self.connections:
            await connection.send_text(message)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    def give_status(self) -> bool:
        return len(self.connections) > 0


class RoomsManager:
    def __init__(self) -> None:
        self.rooms = {}

    def get_room_by_name(self, name: str):
        return self.rooms[name]

    def append_room(self, name: str, room: Room) -> None:
        self.rooms[name] = room

    def check_room(self, name: str) -> bool:
        return name in self.rooms.keys()

    def append_room_connection(self, name: str, websocket: WebSocket):
        room = self.rooms[name]
        room.connections.append(websocket)

    async def connect_room(self, name: str, websocket: WebSocket) -> Room:
        room = self.rooms[name]
        await room.connect(websocket)
        return room

    def close_room(self, name: str) -> None:
        room = self.rooms[name]
        if not (room.give_status()):
            del self.rooms[name]
