from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
    Cookie,
    Query,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from api.wsmanager import Room, Connection
from shemas.room import RoomAuth
from shemas.user import UserBlock
from core.tools import manager, parser, encoder, decoder, database

router = APIRouter()


@router.post("/{name}/auth")
async def room_password_auth(auth: RoomAuth):
    data = jsonable_encoder(auth)
    token, username, password = data["room_token"], data["username"], data["password"]
    room = database.get_room_by_name(token)
    if decoder.verify_password(password, room.password):
        if database.check_user(username, room.id):
            database.create_user(username, False, room.id)
            sessionCookie = encoder.encode_session(token, password, username, "")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"User": data["username"]},
                headers={
                    "Content-Type": "application/json",
                    "Set-Cookie": f"session={sessionCookie}",
                },
            )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"Erorr": "Invalid password"},
        headers={
            "Content-Type": "application/json",
        },
    )


@router.get("/{name}")
async def room(name: str, session: Optional[str] = Cookie(None)):
    hashed_name, room, user = parser.get_room_data(name, session)
    if decoder.verify_session(hashed_name, room.password, session, user.status):
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
                "Users": list(
                    map(
                        lambda user: {
                            "name": user.name,
                            "status": user.status,
                            "online": False,
                        },
                        room.users,
                    )
                ),
            },
            headers={
                "Content-Type": "application/json",
                "Connection": "keep-alive",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"Status": "Invalid session"},
        headers={
            "Content-Type": "application/json",
        },
    )


@router.delete("/{name}")
async def delete_room(name: str, session: Optional[str] = Cookie(None)):
    hashed_name, room, user = parser.get_room_data(name, session)
    if decoder.verify_session(hashed_name, room.password, session, user.status, True):
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


@router.patch("/{name}")
async def block_room_user(
    name: str, user: UserBlock, session: Optional[str] = Cookie(None)
):
    hashed_name, room, user = parser.get_room_data(name, session)
    username = jsonable_encoder(user)["username"]
    if decoder.verify_session(hashed_name, room.password, session, user.status, True):
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
