from fastapi import FastAPI, WebSocket, Request, Header, Cookie, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from sockmanager import WebSocketManager
from utils.temp_dev import Reader
from models import Room
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from utils.crypt import Encoder

encoder = Encoder()
app = FastAPI()

# delete this
templates = {
    'index': Reader('index.html').read_html()
}


@app.get("/")
async def get():
    return HTMLResponse(templates['index'])


@app.post("/")
async def generateRoom(room: Room, cookie: Optional[str] = Cookie(None)):
    try:
        return {
            "Room": JSONResponse(jsonable_encoder(room)),
            "link": encoder.gen_hash_link(jsonable_encoder(room)['name']),
            "password": encoder.hash_password(jsonable_encoder(room)['password'])
        }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": str(error)
            })
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
