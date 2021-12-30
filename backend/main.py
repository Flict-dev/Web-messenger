from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
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
from typing import Optional, List
from utils.crypt import Encoder, Decoder
from utils.helpers import Parser, Reader
from sockmanager import RoomsManager, Room
from models import RoomReq, RoomAuth, MsgKeysCreate, MsgKeysGet
from database import Database
from secrets import token_hex

from fastapi.responses import RedirectResponse

# in prod use token_hex(32)
SECRET_KEY = '9057e8f415a4ed8b2f01deaaad52baf7d30e59604939e3e4cce324444ec4acfb'
URL = 'sqlite:///sqlite.db'

manager = RoomsManager()
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
            hashed_name, plainPassword, 'Admin', encoder.key
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
                "error": error
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
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "Code": 500,
                "error": error
            })


@app.post('/rooms/{name}/auth')
async def validate_room_password(name: str, auth: RoomAuth):
    try:
        hashed_name = parser.parse_link_hash(name)
        json_data = jsonable_encoder(auth)
        room = database.get_room_by_name(hashed_name)
        password, username = json_data['password'], json_data['username']
        if decoder.verify_password(password, room.password):
            if not database.check_user(username):
                database.create_user({
                    "name": username,
                    "admin": False,
                    "room_id": room.id,
                }, room.id)
                sessionCookie = encoder.encode_session(
                    hashed_name, password, username, ''
                )
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
            content={'Erorr': 'Invalid password or username'},
            headers={
                'Content-Type': 'application/json',
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": error
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
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "Code": 500,
                "error": error
            })


@app.post('/rooms/{name}/key')
async def create_msg_key(name: str, keyData: MsgKeysCreate, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            encoded_data = jsonable_encoder(keyData)
            if decoder.verify_admin_session(hashed_name, room.password, session):
                try:
                    database.create_msg_key(
                        room.id, encoded_data['destinied_for'], encoded_data['key']
                    )
                    return JSONResponse(
                        content={"Status": "Msg created"},
                        status_code=status.HTTP_200_OK
                    )
                except ValueError as error:
                    return JSONResponse(
                        content={"error": error},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        return HTMLResponse(
            templates['room_auth'],
            status_code=status.HTTP_302_FOUND,
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "Code": 500,
                "error": error
            })

@app.delete('/rooms/{name}/key')
async def create_msg_key(name: str, keyData: MsgKeysGet, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            encoded_data = jsonable_encoder(keyData)
            if decoder.verify_session(hashed_name, room.password, session):
                try:
                    data = database.get_msg_key(room.id, encoded_data['destinied_for'])
                    database.delete_key(data.id)
                    return JSONResponse(
                        content={"Key": data.key},
                        status_code=status.HTTP_200_OK
                    )
                except ValueError as error:
                    return JSONResponse(
                        content={"error": error},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        return HTMLResponse(
            templates['room_auth'],
            status_code=status.HTTP_302_FOUND,
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "Code": 500,
                "error": error
            })

@app.websocket("/rooms/{name}/")
async def websocket_endpoint(websocket: WebSocket, name: str, session: Optional[str] = Cookie(None)):
    if session:
        if manager.check_room(name):
            manager.append_room_connection(name, websocket)
        else:
            manager.append_room(name, Room(name))
            manager.append_room_connection(name, websocket)
        room = await manager.connect_room(name, websocket)
        user = database.get_room_by_name(parser.parse_link_hash(name))
        username = decoder.decode_session(session)['username']
        msg_key = decoder.decode_session(session)['msg_key']
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    if database.create_message(
                        encoder.encrypt_message(data, str(msg_key).encode()),
                        user.id
                    ):
                        await room.broadcast(f"{username} says: {data}")
                except ValueError:
                    await room.broadcast(f"{username} havent encryption keys")
        except WebSocketDisconnect:
            room.disconnect(websocket)
            await room.broadcast(f"{username} left the chat")
            manager.close_room(name)
