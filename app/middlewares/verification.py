from fastapi import Request, HTTPException, status
from functools import wraps
from app.database.sql import async_session, get_entity_by_id
from app.database.modal import User, UserRoles
from app.middlewares.jwt import JWTAuth

def RequireRole(min_role: UserRoles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            if request is None:
                # 尝试从 args 或 kwargs 中获取 request
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if request is None:
                    request = kwargs.get("request")
            if request is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未能获取到请求对象")
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供有效的JWT令牌")
            token = token[7:]
            payload, error = JWTAuth.decode_token(token)
            if error or not payload:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error["error"] if error else "JWT无效")
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JWT缺少用户ID")
            async with async_session() as session:
                user = await get_entity_by_id(session, User, user_id)
                if not user:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
                if user.jwt != token:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT不匹配")
                if user.role < min_role:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator