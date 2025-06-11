import os
import jwt
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天有效期

class JWTAuth:
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM) #type: ignore
        return token

    @staticmethod
    def decode_token(token: str) -> List[Optional[Dict[str, Any]]]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]) #type: ignore
            return [payload, None]
        except jwt.ExpiredSignatureError:
            return [None, {"error": "令牌已过期"}]
        except jwt.PyJWTError:
            return [None, {"error": "令牌无效"}]
