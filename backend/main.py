from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from sockmanager import WebSocketManager
from helpers.temp_dev import Reader
from models import Room
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()




# delete this
templates = {
    'index': Reader('index.html').read_html()
}

@app.get("/")
async def get():
    return HTMLResponse(templates['index'])


@app.post("/")
async def generateRoom(room: Room):
    print(jsonable_encoder(room))
    return JSONResponse(content=jsonable_encoder(room))
    # roomName, roomPassword = request["name"], request["password"]
    
    # manager = WebSocketManager(roomName)
    # @app.websocket(f"/rooms/{manager}")
    # async def websocket_endpoint(websocket: WebSocket):
    #     await manager.connect(websocket)
    #     try:
    #         while True:
    #             data = await websocket.receive_text()
    #             await manager.broadcast(f"lox: {data}")
    #     except WebSocketDisconnect:
    #         manager.disconnect(websocket)
    #         await manager.broadcast(f"Client left the chat")
