from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from utils.helpers import Parser, Reader
from shemas.room import RoomReq
from core.utils import parser, encoder, database

router = APIRouter()

# delete this
templates = {
    'index': Reader('index.html').read_html(),
    'room': Reader('room.html').read_html(),
    'room_auth': Reader('room_auth.html').read_html(),
}


@router.get('/')
async def home():
    return HTMLResponse(templates['index'], status_code=status.HTTP_200_OK)


@router.post('/')
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
            content={'link': f'/rooms/{link}'},
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
                'Code': 400,
                'error': error
            })
