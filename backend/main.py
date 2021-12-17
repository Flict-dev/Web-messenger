from fastapi import (FastAPI,
                     WebSocket,
                     Request,
                     HTTPException,
                     status,
                     Header,
                     Cookie,
                     )
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from typing import Optional, List
from utils.crypt import Encoder
from utils.helpers import Parser, Reader
from sockmanager import WebSocketManager
from models import RoomReq
from database import Database
from secrets import token_hex

SECRET_KEY = token_hex(32)
URL = 'sqlite:///sqlite.db'

parser = Parser()
encoder = Encoder()
database = Database(URL)
app = FastAPI()

# delete this
templates = {
    'index': Reader('index.html').read_html()
}


@app.get("/")
async def get():
    return HTMLResponse(templates['index'])


@app.post("/")
async def generateRoom(room: RoomReq):
    try:
        plainName, plainPassword = parser.parse_room_data(room)
        link = encoder.gen_hash_link(plainName)
        database.create_room(plainName, encoder.hash_password(plainPassword))

        # return {
        #     "link": ,
        #     "password":
        # }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": str(error)
            })

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
