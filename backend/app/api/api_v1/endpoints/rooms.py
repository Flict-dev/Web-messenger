from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
    Cookie,
    Query,
    Header,
    Depends,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from api.wsmanager import Room, Connection
from schemes.room import RoomAuth
from schemes.user import UserBlock
from core.tools import manager, parser, encoder, decoder, database
from core.config import settings
from pydantic import BaseModel

router = APIRouter()
from fastapi_csrf_protect import CsrfProtect

# from fastapi_csrf_protect.exceptions import CsrfProtectError


class CsrfSettings(BaseModel):
    secret_key: str = settings.CSRF_SECRET_KEY


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@router.post("/{name}/auth")
async def room_password_auth(
    name: str, auth: RoomAuth, x_token: Optional[str] = Header(None)
):
    data = jsonable_encoder(auth)
    username, password = data["username"], data["password"]
    hased_name = parser.parse_link_hash(name)
    room = database.get_room_by_name(hased_name)
    if decoder.verify_password(password, room.password):
        if database.check_user(username, room.id):
            database.create_user(username, False, room.id)
            sessionCookie = encoder.encode_session(
                hased_name, password, username, "", encoder.hash_name(username)
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"User": data["username"]},
                headers={
                    "Content-Type": "application/json",
                    "Cookie": f"session={sessionCookie}",
                },
            )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"Erorr": "Invalid password"},
        headers={"Content-Type": "application/json", "WWW-Authenticate": "Bearer"},
    )


@router.get("/{name}")
async def room(
    name: str,
    authorization: Optional[str] = Header(None),
    csrf_protect: CsrfProtect = Depends(),
):
    hashed_name, room, user = parser.get_room_data(name, authorization)
    if decoder.verify_session(hashed_name, room.password, authorization, user.status):
        enc_messages, messages = database.get_all_messages(room.id), []
        for message in enc_messages:
            messages.append(
                {
                    "Message": message.data,
                    "Created_at": parser.parse_msg_time(message.created_at),
                    "Username": message.user_name,
                }
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "Status": 200,
                "User": user.name,
                "Messages": messages,
                "Users": parser.parse_room_users(list(room.users)),
            },
            headers={
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "X-CSRF-Token": csrf_protect.generate_csrf(),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"Status": "Invalid session"},
        headers={
            "Content-Type": "application/json",
            "WWW-Authenticate": "Bearer",
        },
    )


@router.delete("/{name}")  # ADD Csrf check
async def delete_room(name: str, authorization: Optional[str] = Header(None)):
    hashed_name, room, user = parser.get_room_data(name, authorization)
    if decoder.verify_session(
        hashed_name, room.password, authorization, user.status, True
    ):
        database.delete_room(room.id)
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={"Status": "Room has been deleted"},
            headers={
                "Location": "/",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"User not admin"}
    )


@router.patch("/{name}")  # ADD Csrf check
async def block_room_user(
    name: str, user: UserBlock, authorization: Optional[str] = Header(None)
):
    hashed_name, room, user = parser.get_room_data(name, authorization)
    username = jsonable_encoder(user)["username"]
    if decoder.verify_session(
        hashed_name, room.password, authorization, user.status, True
    ):
        await database.block_user(username, room.id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"Status": "User has been blocked"},
        )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"Status": "User not admin"}
    )


@router.websocket("/{name}")
async def websocket_endpoint(
    websocket: WebSocket, name: str, session: Optional[str] = Query(None)
):
    hashed_name, room_obj, user = parser.get_room_data(name, session)
    if decoder.verify_session(hashed_name, room_obj.password, session, user.status):
        manager.append_room(name, Room(name))
        connection = Connection(user.name, websocket)
        try:
            manager.append_room_connection(name, connection)
            room = await manager.connect_room(name, connection)
            try:
                while True:
                    data = await websocket.receive_json()
                    database.create_message(data["message"], user.id, user.name)
                    await room.broadcast(200, data["message"], user.name)
            except WebSocketDisconnect:
                await room.disconnect(connection)
                manager.close_room(name)
                await room.broadcast(202, f"{user.name} left chat", user.name)
        except RuntimeError:
            manager.delete_connections(name)
