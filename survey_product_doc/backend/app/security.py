# backend/app/security.py

from datetime import datetime, timedelta, timezone
from typing import Union, Any
from jose import jwt, JWTError
from backend.app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # 导入 OAuth2PasswordBearer
from backend.app.schemas.token import TokenData # 导入 TokenData
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services import user_service # 导入 user_service

# 定义 OAuth2PasswordBearer 实例，用于从请求中提取令牌
# tokenUrl 指向你的登录接口，FastAPI 会自动在 Swagger UI 中生成认证输入框
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login/access-token")

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    创建 JWT 访问令牌。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Union[dict, None]:
    """
    验证 JWT 令牌。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI 依赖函数，用于获取当前登录用户。
    - 从请求头中提取令牌。
    - 验证令牌。
    - 从数据库中获取用户对象。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        username: Union[str, None] = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise credentials_exception

    user = user_service.get_user_by_username(db, username=username)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_optional(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI 依赖函数，用于获取当前登录用户（可选）。
    - 如果没有令牌或令牌无效，返回 None。
    - 用于支持匿名访问的端点。
    """
    if not token:
        return None

    try:
        payload = verify_token(token)
        if payload is None:
            return None
        
        username: Union[str, None] = payload.get("sub")
        if username is None:
            return None

        token_data = TokenData(username=username)
        
    except JWTError:
        return None
    except Exception as e:
        return None

    user = user_service.get_user_by_username(db, username=username)
    
    if user is None:
        return None
    
    return user

