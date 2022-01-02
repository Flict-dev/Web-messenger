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
from models import RoomReq, RoomAuth, MsgKeysCreate, MsgKeysGet, UserBlock
from database import Database
from secrets import token_hex

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
        plainName, plainPassword = await parser.parse_room_data(room)
        hashed_name = await encoder.hash_name(plainName)
        link = encoder.gen_hash_link(hashed_name)
        await database.create_room(
            {
                'name': hashed_name,
                'password': encoder.hash_password(plainPassword)
            }
        )
        sessionCookie = await encoder.encode_session(
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
async def room_session_auth(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            user = await database.get_user_by_name(decoder.decode_session(session)['username'])
            if decoder.verify_session(hashed_name, room.password, session) and user.status:
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"Auth": True},
                    headers={
                        'Content-Type': 'application/json',
                        'Location': f'/rooms/{name}',
                    }
                )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Content-Type': 'application/json',
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "Error": error
            })


@app.post('/rooms/{name}/auth')
async def room_password_auth(name: str, auth: RoomAuth):
    try:
        hashed_name = await parser.parse_link_hash(name)
        json_data = await jsonable_encoder(auth)
        room = await database.get_room_by_name(hashed_name)
        password, username = json_data['password'], json_data['username']
        if decoder.verify_password(password, room.password):
            if not database.check_user(username, room.id):
                database.create_user({
                    "name": username,
                    "admin": False,
                    "room_id": room.id,
                }, room.id)
                sessionCookie = await encoder.encode_session(
                    hashed_name, password, username, ''
                )
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={'User': username},
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
                "Error": error
            })


@app.get('/rooms/{name}')
async def room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            decoded_session = await decoder.decode_session(session)
            user = await database.get_user_by_name(decoded_session['username'])
            if decoder.verify_session(hashed_name, room.password, session) and user.status:
                encoded_messages, messages = database.get_all_messages(room.id), {
                }
                for message in encoded_messages:
                    user = database.get_user_by_id(message.user_id)
                    messages[user.name] = {
                        'Message': decoder.dcrypt_message(message.data, decoded_session['msg_key']),
                        'Created_at': parser.parse_msg_time(message.created_at)
                    }
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        'User': decoded_session['username'],
                        'Messages': messages
                    },
                    headers={
                        'Content-Type': 'application/json',
                        'Connection': 'keep-alive'
                    }
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "Error": error
            })


@app.delete('/rooms/{name}')
async def delete_room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            user = await database.get_user_by_name(decoder.decode_session(session)['username'])
            if decoder.verify_session(hashed_name, room.password, session, True) and user.status:
                await database.delete_room(room.id)
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"Status": "Room has been deleted"},
                    headers={
                        'Location': '/',
                    }
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "Error": error
            })


@app.patch('/rooms/{name}')
async def block_room_user(name: str, user: UserBlock, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            username = jsonable_encoder(user)['username']
            user = await database.get_user_by_name(username)
            if decoder.verify_session(hashed_name, room.password, session, True) and user.status:
                await database.block_user(username, room.id)
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"Status": "User has been blocked"},
                    headers={
                        'Location': '/',
                    }
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "Error": error
            })


@app.post('/rooms/{name}/key')
async def create_msg_key(name: str, keyData: MsgKeysCreate, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            encoded_data = await jsonable_encoder(keyData)
            user = await database.get_user_by_name(decoder.decode_session(session)['username'])
            if decoder.verify_session(hashed_name, room.password, session, True) and user.status:
                database.create_msg_key(
                    room.id, encoded_data['destinied_for'], encoded_data['key']
                )
                return JSONResponse(
                    content={"Status": "Msg created"},
                    status_code=status.HTTP_200_OK
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "Error": error
            })


@app.delete('/rooms/{name}/key')
async def delete_msg_key(name: str, keyData: MsgKeysGet, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = await parser.parse_link_hash(name)
            room = await database.get_room_by_name(hashed_name)
            encoded_data = jsonable_encoder(keyData)
            user = await database.get_user_by_name(decoder.decode_session(session)['username'])
            if decoder.verify_session(hashed_name, room.password, session) and user.status:
                try:
                    data = database.get_msg_key(
                        room.id, encoded_data['destinied_for']
                    )
                    key_session = decoder.session_add_key(session, data.key)
                    database.delete_key(data.id)
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        headers={
                            'Set-Cookie': f'session={key_session}',
                        }
                    )
                except ValueError as error:
                    return JSONResponse(
                        content={"error": error},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                'Location': f'/rooms/{name}/auth',
                'Connection': 'close'
            }
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Code": 400,
                "error": error
            })


@app.websocket("/rooms/{name}/")
async def websocket_endpoint(websocket: WebSocket, name: str, session: Optional[str] = Cookie(None)):
    if session:
        decoded_session = await decoder.decode_session(session)
        username = decoded_session['username']
        hashed_name = await parser.parse_link_hash(name)
        room_obj = await database.get_room_by_name(hashed_name)
        user = await database.get_user_by_name(username, room_obj.id)
        if decoder.verify_session(hashed_name, room_obj.password, session) and user.status:
            if manager.check_room(name):
                manager.append_room_connection(name, websocket)
            else:
                manager.append_room(name, Room(name))
                manager.append_room_connection(name, websocket)
            room = await manager.connect_room(name, websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        if database.create_message(
                                encoder.encrypt_message(
                                    data, str(
                                        decoded_session['msg_key']).encode()
                                ), user.id):
                            await room.broadcast(f"{username} says: {data}")
                    except ValueError:
                        await room.broadcast(f"{username} havent encryption keys")
            except WebSocketDisconnect:
                room.disconnect(websocket)
                await room.broadcast(f"{username} left the chat")
                manager.close_room(name)
