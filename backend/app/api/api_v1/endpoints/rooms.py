from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
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
from shemas.msg_key import MsgKeysCreate
from core.utils import manager, parser, encoder, decoder, database

router = APIRouter()


@router.get("/{name}/auth")
async def room_session_auth(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            user = database.get_user_by_name(
                decoder.decode_session(session)["username"], room.id
            )
            if (
                decoder.verify_session(hashed_name, room.password, session)
                and user.status
            ):
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"Auth": True},
                    headers={
                        "Content-Type": "application/json",
                        "Location": f"api/v1/rooms/{name}",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"Unauthorized": "Session doesn't exist"},
            headers={
                "Content-Type": "application/json",
            },
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.post("/{name}/auth")
async def room_password_auth(name: str, auth: RoomAuth):
    try:
        hashed_name = parser.parse_link_hash(name)
        json_data = jsonable_encoder(auth)
        room = database.get_room_by_name(hashed_name)
        password, username = json_data["password"], json_data["username"]
        if decoder.verify_password(password, room.password):
            if not database.check_user(username, room.id):
                database.create_user(
                    {
                        "name": username,
                        "admin": False,
                        "room_id": room.id,
                    },
                    room.id,
                )
                sessionCookie = encoder.encode_session(
                    hashed_name, password, username, ""
                )
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"User": username},
                    headers={
                        "Content-Type": "application/json",
                        "Set-Cookie": f"session={sessionCookie}",
                        "Location": f"/rooms/{name}",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"Erorr": "Invalid password or username"},
            headers={
                "Content-Type": "application/json",
            },
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.get("/{name}")
async def room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            decoded_session = decoder.decode_session(session)
            user = database.get_user_by_name(decoded_session["username"], room.id)
            if (
                decoder.verify_session(hashed_name, room.password, session)
                and user.status
            ):
                encoded_messages, messages = database.get_all_messages(room.id), {}
                for message in encoded_messages:
                    user = database.get_user_by_id(message.user_id)
                    messages[user.name] = {
                        "Message": message.data,
                        "Created_at": parser.parse_msg_time(message.created_at),
                        "Status": user.status,
                    }
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "Status": 200,
                        "User": decoded_session["username"],
                        "Messages": messages,
                        "Users": list(map(lambda user: user.name, room.users)),
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Connection": "keep-alive",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.delete("/{name}")
async def delete_room(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            user = database.get_user_by_name(
                decoder.decode_session(session)["username"], room.id
            )
            if (
                decoder.verify_session(hashed_name, room.password, session, True)
                and user.status
            ):
                database.delete_room(room.id)
                return JSONResponse(
                    status_code=status.HTTP_302_FOUND,
                    content={"Status": "Room has been deleted"},
                    headers={
                        "Location": "/",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.patch("/{name}")
async def block_room_user(
    name: str, user: UserBlock, session: Optional[str] = Cookie(None)
):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            username = jsonable_encoder(user)["username"]
            user = database.get_user_by_name(username, room.id)
            if (
                decoder.verify_session(hashed_name, room.password, session, True)
                and user.status
            ):
                await database.block_user(username, room.id)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"Status": "User has been blocked"},
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.post("/{name}/key")
async def create_msg_key(
    name: str, keyData: MsgKeysCreate, session: Optional[str] = Cookie(None)
):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            encoded_data = jsonable_encoder(keyData)
            user = database.get_user_by_name(
                decoder.decode_session(session)["username"], room.id
            )
            if (
                decoder.verify_session(hashed_name, room.password, session, True)
                and user.status
            ):
                database.create_msg_key(
                    room.id, encoded_data["destinied_for"], encoded_data["key"]
                )
                return JSONResponse(
                    content={"Status": "Msg created"}, status_code=status.HTTP_200_OK
                )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.delete("/{name}/key")
async def delete_msg_key(name: str, session: Optional[str] = Cookie(None)):
    try:
        if session:
            hashed_name = parser.parse_link_hash(name)
            room = database.get_room_by_name(hashed_name)
            decoded_session = decoder.decode_session(session)
            user = database.get_user_by_name(decoded_session["username"], room.id)
            if (
                decoder.verify_session(hashed_name, room.password, session)
                and user.status
            ):
                try:
                    data = database.get_msg_key(room.id, decoded_session["username"])
                    key_session = decoder.session_add_key(session, data.key)
                    await database.delete_key(data.id)
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"Status": "The encryption key was received"},
                        headers={
                            "Set-Cookie": f"session={key_session}",
                        },
                    )
                except ValueError as error:
                    return JSONResponse(
                        content={"error": error},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        return JSONResponse(
            status_code=status.HTTP_302_FOUND,
            content={"Unauthorized": "Session doesn't exist"},
            headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error}
        )


@router.websocket("/{name}")
async def websocket_endpoint(
    websocket: WebSocket, name: str, session: Optional[str] = Query(None)
):
    if session:
        decoded_session = decoder.decode_session(session)
        username = decoded_session["username"]
        hashed_name = parser.parse_link_hash(name)
        room_obj = database.get_room_by_name(hashed_name)
        user = database.get_user_by_name(username, room_obj.id)
        if (
            decoder.verify_session(hashed_name, room_obj.password, session)
            and user.status
        ):
            if manager.check_room(name):
                connection = Connection(username, websocket)
                manager.append_room_connection(name, connection)
            else:
                manager.append_room(name, Room(name))
                connection = Connection(username, websocket)
                manager.append_room_connection(name, connection)
            room = await manager.connect_room(name, connection)
            try:
                while True:
                    data = await websocket.receive_json()
                    data = dict(data)
                    try:
                        if database.create_message(data, user.id):
                            await room.broadcast(200, data["message"], username)
                    except ValueError:
                        await room.broadcast(
                            204, f"{username} havent encryption keys", username
                        )
            except WebSocketDisconnect:
                await room.disconnect(connection)
                manager.close_room(name)
                await room.broadcast(202, f"{username} left chat", username)
                