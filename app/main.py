from app.apis.base import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.db.utils import check_db_connected
from app.db.utils import check_db_disconnected
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.base import router as web_app_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


def create_tables():
    Base.metadata.create_all(bind=engine)

def cors_setup(app):
    origins = [
    "http://localhost:8080",
    #"http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    cors_setup(app)
    include_router(app)
    configure_static(app)
    create_tables()
    return app


app = start_application()


@app.on_event("startup")
async def app_startup():
    await check_db_connected()


@app.on_event("shutdown")
async def app_shutdown():
    await check_db_disconnected()
