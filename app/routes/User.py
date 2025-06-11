from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.database.sql import async_session
from app.database.modal import User, UserRoles
from app.middlewares.jwt import JWTAuth
from app.middlewares.verification import RequireRole
from utils.logging import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register")
async def register(user_data: dict):
    """用户注册接口"""
    async with async_session() as session:
        # 检查用户名是否已存在
        existing_user = await User.get_by_username(session, user_data["username"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 创建新用户
        new_user = User(
            username=user_data["username"],
            password=user_data["password"],  # 实际应用中应该加密
            role=UserRoles.STUDENT
        )
        session.add(new_user)
        await session.commit()
        
        logger.info(f"New user registered: {user_data['username']}")
        return {"message": "User registered successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录接口"""
    async with async_session() as session:
        user = await User.authenticate(
            session,
            username=form_data.username,
            password=form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = JWTAuth.create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{user_id}")
@RequireRole(UserRoles.STUDENT)
async def get_user(user_id: int):
    """获取用户信息接口"""
    async with async_session() as session:
        user = await User.get_by_id(session, user_id)
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