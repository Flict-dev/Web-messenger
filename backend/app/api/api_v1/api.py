from fastapi import APIRouter
from api.api_v1.endpoints import rooms, base

apirouter = APIRouter()
apirouter.include_router(base.router, tags=["home"])
apirouter.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
