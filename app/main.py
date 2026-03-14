from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import api_router
from core.config import settings

import logging

from fastapi.responses import JSONResponse
from core.exceptions import AppException
from core.response import error_response

from core.database import engine, Base
from sqlalchemy import text

# import all models for automatically creating table in database
from models.user import *


logging.basicConfig(level=logging.INFO)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()



@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.error_code, exc.error_desc)
    )

# from core.config import settings
# print("Loaded DB:", settings.DB_HOST)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS accounts"))
        await conn.run_sync(Base.metadata.create_all)