from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
    HTTPException,
    Query,
    Header,
    Depends,
)
from fastapi.encoders import jsonable_encoder as pydantic_decoder
from fastapi.responses import JSONResponse
from typing import Optional
from api.wsmanager import Room, Connection
from schemes.room import RoomAuth
from schemes.user import UserBlock
from core.tools import manager, parser, encoder, decoder, database
from core.config import settings
from pydantic import BaseModel
from time import time

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
    data = pydantic_decoder(auth)
    username, password = data["username"], data["password"]
    hased_name = parser.parse_link_hash(name)
    room = database.get_room_by_name(hased_name)
    if decoder.verify_hash(password, room.password):
        if not decoder.verify_hash(username, x_token):
            user = database.create_user(username, False, room.id)
        else:
            user = database.get_user_by_name(username, room.id)
        sessionCookie = encoder.encode_session(
            hased_name, user.id, room.id, user.admin, encoder.hash_text(username)
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"User": data["username"]},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"session={sessionCookie}",
                "X-Token": encoder.hash_text(username),
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"Erorr": "Invalid password"},
        headers={"Content-Type": "application/json", "WWW-Authenticate": "Bearer"},
    )


@router.get("/{name}")
async def room(
    name: str,
    authorization: Optional[str] = Header(None),
    csrf_protect: CsrfProtect = Depends(),
):
    hashed_name, room, user = parser.get_room_data(name, authorization)
    if decoder.verify_session(hashed_name, authorization, user.status):
        enc_messages, messages = database.get_all_messages(room), []
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
                "X-Token": encoder.hash_text(user.name),
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"Status": "Invalid session"},
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
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail={"User not admin"}
    )


@router.patch("/{name}")  # ADD Csrf check
async def block_room_user(
    name: str, user: UserBlock, authorization: Optional[str] = Header(None)
):
    hashed_name, room, user = parser.get_room_data(name, authorization)
    username = pydantic_decoder(user)["username"]
    if decoder.verify_session(
        hashed_name, room.password, authorization, user.status, True
    ):
        await database.block_user(username, room.id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"Status": "User has been blocked"},
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail={"Status": "User not admin"}
    )


@router.websocket("/{name}")
async def websocket_endpoint(
    websocket: WebSocket, name: str, session: Optional[str] = Query(None)
):
    hashed_name, room_obj, user = parser.get_room_data(name, session)
    if decoder.verify_session(hashed_name, session, user.status):
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
