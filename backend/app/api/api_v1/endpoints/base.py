from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from shemas.room import RoomReq
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
    plainName, plainPassword = parser.parse_room_data(room)
    hashed_name = encoder.hash_name(plainName)
    hashed_password = encoder.hash_password(plainPassword)
    link = encoder.gen_hash_link(hashed_name)
    if hashed_password:
        database.create_room(hashed_name, hashed_password)
        sessionCookie = encoder.encode_session(
            hashed_name, plainPassword, "Admin", encoder.key
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"link": f"/rooms/{link}"},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"session={sessionCookie}",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Eliot hates when the password is too simple"},
        headers={
            "Content-Type": "application/json",
        },
    )
