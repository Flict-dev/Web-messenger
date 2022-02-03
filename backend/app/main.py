from fastapi import FastAPI
from api.api_v1.api import apirouter
from core.config import settings
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, debug=settings.DEBUG
)

origins = [
    "http://localhost:3000",
    "http://localhost",
]


def messenger_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Web Messenger API",
        version="1.0.0",
        description="First app version",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Cookie"],
)

app.openapi = messenger_openapi
app.include_router(apirouter, prefix=settings.API_V1_STR)
