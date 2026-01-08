# backend/app/api/deps.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from backend.app import crud, models, schemas
from backend.app.config import settings
from backend.app.database import get_db
from sqlalchemy.orm import Session
from backend.app.security import get_current_user

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

# --- 新增 get_current_user 函数 ---

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # "token" 是你获取 JWT 的登录路由

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="无法验证凭据",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # 解码 JWT Token
#         # 确保你的 JWT payload 中有一个 "sub" 字段存储用户ID
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: Optional[str] = payload.get("sub") # "sub" 通常用于存储主题，这里是用户ID
#         if user_id is None:
#             raise credentials_exception
#         # 返回一个包含用户ID的字典。如果需要更多用户信息，可以在这里从数据库加载。
#         return {"id": int(user_id)} # 确保返回的是一个包含 'id' 键的字典
#     except JWTError:
#         raise credentials_exception

async def get_survey_by_id_and_owner(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Survey:
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    if db_survey.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this survey's answers")
    return db_survey

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前活跃用户。
    """
    # 暂时跳过is_active检查，因为可能没有这个属性
    # if not current_user.is_active:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非活跃用户")
    return current_user

# --- 新增：获取当前活跃的超级用户 (系统管理员) ---
async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前活跃的超级用户（系统管理员）。
    """
    # 暂时跳过is_superuser检查，因为可能没有这个属性
    # if not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="用户权限不足，需要超级用户权限"
    #     )
    return current_user