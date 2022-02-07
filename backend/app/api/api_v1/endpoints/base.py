from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from schemes.room import RoomReq
from core.tools import encoder, database

router = APIRouter()


@router.post("/")
async def create_room(room: RoomReq) -> JSONResponse:
    h_name, h_pswd = encoder.hash_room_data(room)
    room = database.create_room(h_name, h_pswd)
    user = database.create_user("Admin", True, room)
    link = encoder.gen_hash_link(h_name)
    sessionCookie = encoder.encode_session(h_name, user.id, room.id, True, encoder.key)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"link": f"/rooms/{link}"},
        headers={
            "Content-Type": "application/json",
            "Cookie": f"session={sessionCookie}",
            "X-Token": encoder.hash_text("Admin"),
        },
    )
