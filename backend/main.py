from fastapi import (
    FastAPI,
    WebSocket,
    Request,
    HTTPException,
    status,
    Header,
    Cookie,
    Response
)

from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from typing import Optional, List
from utils.crypt import Encoder, Decoder
from utils.helpers import Parser, Reader
from sockmanager import WebSocketManager
from models import RoomReq, RoomAuth
from database import Database
from secrets import token_hex

from fastapi.responses import RedirectResponse

# in prod use token_hex(32)
SECRET_KEY = '9057e8f415a4ed8b2f01deaaad52baf7d30e59604939e3e4cce324444ec4acfb'
URL = 'sqlite:///sqlite.db'

parser = Parser()
encoder = Encoder(SECRET_KEY)
decoder = Decoder(SECRET_KEY)
database = Database(URL)
app = FastAPI()

# delete this
templates = {
    'index': Reader('index.html').read_html(),
    'room': Reader('room.html').read_html(),
    'room_auth': Reader('room_auth.html').read_html(),
}


@app.get("/")
async def home():
    return HTMLResponse(templates['index'], status_code=status.HTTP_200_OK)


@app.post("/")
async def create_room(room: RoomReq):
    try:
        plainName, plainPassword = parser.parse_room_data(room)
        hashed_name = encoder.hash_name(plainName)
        link = encoder.gen_hash_link(hashed_name)
        database.create_room(
            {
                'name': hashed_name,
                'password': encoder.hash_password(plainPassword)
            }
        )
        sessionCookie = encoder.encode_session(
            hashed_name, plainPassword, 'Admin'
        )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"link": f'/rooms/{link}'},
            headers={
                'Content-Type': 'application/json',
                'Set-Cookie': f'session={sessionCookie}',
                'Location': f'/rooms/{link}/auth'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": str(error)
            })


@app.get('/rooms/{name}/auth')
async def room_auth(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            if decoder.verify_session(hashed_name, room.password, session):
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"auth": True},
                    headers={
                        'Content-Type': 'application/json',
                        'Location': f'/rooms/{name}',
                    }
                )
        return HTMLResponse(
            templates['room_auth'],
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
            })


@app.post('/rooms/{name}/auth')
async def validate_room_password(name: str, auth: RoomAuth):
    try:
        hashed_name = parser.parse_link_hash(name)
        json_data = jsonable_encoder(auth)
        room = database.get_room_by_name(hashed_name)
        password, username = json_data['password'], json_data['username']
        if decoder.verify_password(password, room.password):
            sessionCookie = encoder.encode_session(
                hashed_name, password, username
            )
            if not database.check_user(username):
                database.create_user({
                    "name": username,
                    "admin": False,
                    "room_id": room.id,
                })
            return JSONResponse(
                status_code=status.HTTP_302_FOUND,
                content={'Auth': True},
                headers={
                    'Content-Type': 'application/json',
                    'Set-Cookie': f'session={sessionCookie}',
                    'Location': f'/rooms/{name}'
                }
            )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'Erorr': 'Invalid password'},
            headers={
                'Content-Type': 'application/json',
            }
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
            })


@app.get('/rooms/{name}')
async def room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            if decoder.verify_session(hashed_name, room.password, session):
                return HTMLResponse(
                    templates['room'],
                    status_code=status.HTTP_200_OK,
                    headers={
                        'Connection': 'keep-alive'
                    }
                )
        return HTMLResponse(
            templates['room_auth'],
            status_code=status.HTTP_302_FOUND,
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
            })


@app.post('/rooms/{name}')
async def start_room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            if decoder.verify_session(hashed_name, room.password, session):
                manager = WebSocketManager(name)

                @app.websocket(f"/rooms/{manager}/")
                async def websocket_endpoint(websocket: WebSocket):
                    await manager.connect(websocket)
                    while True:
                        data = await websocket.receive_text()
                        await manager.broadcast(f"lox: {data}")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
            })
