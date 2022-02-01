from fastapi import APIRouter, status, Request, HTTPException
from fastapi.responses import JSONResponse
from schemes.room import RoomReq
from core.tools import parser, encoder, database

router = APIRouter()


@router.get("/")
async def home(request: Request):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ip": f"{request.client.host}"},
    )


@router.post("/")
async def create_room(room: RoomReq):
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
