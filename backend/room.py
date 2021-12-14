from fastapi import WebSocket
from typing import List

class WebSocketManager:
    def __init__(self, name: str) -> None:
        self.name = name
        self.connections: List[WebSocket] = []

    def __str__(self):
        return self.name
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)
    
    async def broadcast(self, message: str) -> None:
        for connection in self.connections:
            await connection.send_text(message)

    async def disconnect(self, websocket: WebSocket) -> None:
      self.connections.remove(websocket)
      await self.broadcast('Client leave')
    
