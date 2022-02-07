from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
    HTTPException,
    Request,
    Query,
    Header,
    Depends,
)
from fastapi.encoders import jsonable_encoder as pydantic_decoder
from core.tools import manager, parser, encoder, decoder, database
from fastapi_csrf_protect import CsrfProtect
from fastapi.responses import JSONResponse
from api.wsmanager import Room, Connection
from api.wshandler import WsHandler
from schemes.room import RoomAuth
from core.config import settings
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class CsrfSettings(BaseModel):
    secret_key: str = settings.CSRF_SECRET_KEY


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@router.post("/{name}/auth")
async def room_password_auth(
    name: str,
    auth: RoomAuth,
    x_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> JSONResponse or HTTPException:
    msg_key = decoder.get_key(authorization) if authorization else ""
    data = pydantic_decoder(auth)
    username, password = data["username"], data["password"]
    hased_name = parser.parse_link_hash(name)
    room = database.get_room_by_name(hased_name)
    if decoder.verify_hash(password, room.password):
        if x_token:
            if decoder.verify_hash(username, x_token):
                user = database.get_user_by_name(username, room.id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"Status": "Invalid username or password"},
                )
        else:
            user = database.create_user(username, False, room)
        sessionCookie = encoder.encode_session(
            hased_name, user.id, room.id, user.admin, msg_key
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"User": username},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"session={sessionCookie}",
                "X-Token": encoder.hash_text(username),
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"Error": "Invalid username or password"},
        headers={"Content-Type": "application/json", "WWW-Authenticate": "Bearer"},
    )


@router.get("/{name}")
async def room(
    name: str,
    authorization: Optional[str] = Header(None),
    csrf_protect: CsrfProtect = Depends(),
) -> JSONResponse or HTTPException:
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


@router.delete("/{name}")
async def delete_room(
    request: Request,
    name: str,
    authorization: Optional[str] = Header(None),
    csrf_protect: CsrfProtect = Depends(),
) -> JSONResponse or HTTPException:
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    hashed_name, room, user = parser.get_room_data(name, authorization)
    if decoder.verify_session(hashed_name, authorization, user.status, True):
        database.delete_room(room)
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


@router.websocket("/{name}")
async def websocket_endpoint(
    websocket: WebSocket, name: str, session: Optional[str] = Query(None)
) -> None:
    hashed_name, room_obj, user = parser.get_room_data(name, session)
    if decoder.verify_session(hashed_name, session, user.status):
        decoded_session = decoder.decode_session(session)
        manager.append_room(name, Room(name))
        connection = Connection(user.name, session, websocket)
        try:
            manager.append_room_connection(name, connection)
            room = await manager.connect_room(name, connection)
            room_hadnler = WsHandler(room, connection)
            try:
                while True:
                    data = await websocket.receive_json()
                    hadnleFunc = room_hadnler.hadnlers(data["status"])
                    await hadnleFunc(
                        {
                            "username": data["username"],
                            "message": data["message"],
                            "admin": decoded_session["admin"],
                            "room": room_obj,
                            "user": user,
                        }
                    )
            except WebSocketDisconnect:
                await room.disconnect(connection)
                manager.close_room(name)
                await room.broadcast(202, f"{user.name} left chat", user.name)
        except RuntimeError:
            manager.delete_connections(name)
