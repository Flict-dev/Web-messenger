from fastapi import FastAPI
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
app = FastAPI()

html = ""
with open('index.html', 'r') as f:
    html = f.read()

@app.get("/")
async def get():
    return HTMLResponse(html) 


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: List[WebSocket] = []
        

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str) -> None:
        print(self.connections) 
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(f"Client {client_id}: {data}")