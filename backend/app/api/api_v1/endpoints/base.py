from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Request
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
async def home(request: Request):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'ip': f'{request.client.host}'},
    )


@router.post('/')
async def create_room(room: RoomReq):
        plainName, plainPassword = parser.parse_room_data(room)
        hashed_name = encoder.hash_name(plainName)
        hashed_password = encoder.hash_password(plainPassword)
        link = encoder.gen_hash_link(hashed_name)
        if hashed_password:
            database.create_room(
                {
                    'name': hashed_name,
                    'password': hashed_password
                }
            )
            sessionCookie = encoder.encode_session(
                hashed_name, plainPassword, 'Admin', encoder.key
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={'link': f'/rooms/{link}'},
                headers={
                    'Content-Type': 'application/json',
                    'Set-Cookie': f'session={sessionCookie}',
                }
            )
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'error': 'Eliot hates when the password is too simple'
                },
                headers={
                    'Content-Type': 'application/json',
                }
            )
