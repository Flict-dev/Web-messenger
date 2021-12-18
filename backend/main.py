from fastapi import (FastAPI,
                     WebSocket,
                     Request,
                     HTTPException,
                     status,
                     Header,
                     Cookie,
                     Response
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

from fastapi.responses import RedirectResponse

SECRET_KEY = token_hex(32)
URL = 'sqlite:///sqlite.db'

parser = Parser()
encoder = Encoder(SECRET_KEY)
database = Database(URL)
app = FastAPI()

# delete this
templates = {
    'index': Reader('index.html').read_html(),
    'room': Reader('room.html').read_html()
}


@app.get("/")
async def get():
    return HTMLResponse(templates['index'])


@app.post("/")
async def generateRoom(room: RoomReq):
    try:
        plainName, plainPassword = parser.parse_room_data(room)
        link = encoder.gen_hash_link(plainName)
        database.create_room(
            {
                'name': plainName,
                'password': encoder.hash_password(plainPassword)
            }
        )
        sessionCookie = encoder.create_session(
            plainName, plainPassword, True
        )
        return JSONResponse(
            status_code=status.HTTP_301_MOVED_PERMANENTLY,
            content={"link": f'/rooms/{link}'},
            headers={
                'Content-Type': 'application/json',
                'Set-Cookie': f'session={sessionCookie}',
                'Location': f'/rooms/{link}'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": str(error)
            })


@app.get('/rooms/{name}')
async def room(name: str):
    return HTMLResponse(templates['room'])


@app.post('/rooms/{name}')
async def start_room(name: str):
    manager = WebSocketManager(name)
    @app.websocket(f"/rooms/{manager}/")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"lox: {data}")
