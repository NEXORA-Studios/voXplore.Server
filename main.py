import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.sql import init_db
from app.routes import Base, User
from utils.logging import LoggerFactory

# Logger
logger = LoggerFactory(name="Main")

# MySQL 数据库初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("初始化 SQLite 数据库")
    await init_db()
    logger.info("SQLite 数据库初始化完成")
    yield

app = FastAPI(title="voXplore Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.20.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Base.router)
app.include_router(User.router)
