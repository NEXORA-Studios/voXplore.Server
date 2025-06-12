from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel
import hashlib

from app.database.sql import async_session, create_entity
from app.database.modal import Account, UserRoles
from app.middlewares.jwt import JWTAuth
from app.middlewares.verification import RequireRole
from utils.logging import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

async def get_db():
    async with async_session() as session:
        yield session

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    username: str
    email: str

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Account).where(Account.username == data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already registered")
    hashed_pwd = hashlib.sha256(data.password.encode()).hexdigest()
    user = Account(username=data.username, password_hash=hashed_pwd, email=data.email, role=UserRoles.STUDENT)
    await create_entity(db, user)
    return {"msg": "Successful", "user_id": user.id}

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Account).where(Account.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    if user.password_hash != hashlib.sha256(data.password.encode()).hexdigest():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invaild Credentials")
    # 签发 JWT
    payload = {"user_id": user.id, "role": user.role}
    token = JWTAuth.create_access_token(payload)
    user.jwt = token
    await db.commit()
    return {"msg": "Successful", "username": user.username, "user_id": user.id, "role": user.role, "token": token}

@router.get("/users/{user_id}")
@RequireRole(UserRoles.STUDENT)
async def get_user(user_id: int):
    """获取用户信息接口"""
    async with async_session() as session:
        user = await Account.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.debug(f"Retrieved user info for ID: {user_id}")
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }