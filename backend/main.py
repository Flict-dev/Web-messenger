from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from room import WebSocketManager
app = FastAPI()

html = ""
with open('index.html', 'r') as f:
    html = f.read()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.post("/generate-room")
async def create(name: Request):
    res = await name.json()
    manager = WebSocketManager(str(res["name"]))

    @app.websocket(f"/rooms/{manager}")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        while True:
            try:
                data = await websocket.receive_text()
                await manager.broadcast(f"lox: {data}")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                await manager.broadcast(f"Client left the chat")
    