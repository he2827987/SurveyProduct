# backend/app/api/user_api.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from backend.app.schemas.token import Token # 导入 Token schema
from backend.app.services import user_service
from backend.app.security import create_access_token # <-- 注意这里的导入路径
from datetime import timedelta
from backend.app.security import create_access_token, get_current_user
from backend.app.config import settings # <-- 注意这里的导入路径
from backend.app.models.user import User as UserModel

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    获取当前登录用户的信息。
    - 需要有效的 JWT 访问令牌。
    """
    # 补充 organization_name 便于前端显示
    if current_user.organization_id:
        try:
            from backend.app import crud
            org = crud.get_organization(get_db(), org_id=current_user.organization_id)  # type: ignore
            if org:
                setattr(current_user, "organization_name", org.name)
        except Exception:
            pass
    return current_user
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户。
    - 如果用户名或邮箱已存在，则返回 400 错误。
    - 成功注册后返回用户基本信息。
    """
    db_user_by_username = user_service.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user_by_email = user_service.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = user_service.create_user(db=db, user=user)
    return new_user

@router.post("/login/access-token", response_model=Token) # 修改 response_model 为 Token
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    用户登录并获取访问令牌。
    - 验证用户名和密码。
    - 成功则返回 JWT 访问令牌。
    """
    user = user_service.get_user_by_username(db, username=username)
    if not user:
        user = user_service.get_user_by_email(db, email=username)
    if not user or not user_service.verify_password(password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, # sub (subject) 通常是用户唯一标识
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(user_service.User).offset(skip).limit(limit).all()
    return users

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的信息。
    - 需要有效的 JWT 访问令牌。
    - 只能更新自己的信息。
    """
    updated_user = user_service.update_user(db=db, user_id=current_user.id, user_update=user_update)
    if updated_user and updated_user.organization_id:
        try:
            org = crud.get_organization(db, org_id=updated_user.organization_id)
            if org:
                setattr(updated_user, "organization_name", org.name)
        except Exception:
            pass
    return updated_user

@router.put("/me/password")
async def change_current_user_password(
    password_data: dict,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前登录用户的密码。
    - 需要有效的 JWT 访问令牌。
    - 需要提供当前密码进行验证。
    """
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")
    
    if not old_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password and new password are required"
        )
    
    # 验证当前密码
    if not user_service.verify_password(old_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # 更新密码
    updated_user = user_service.update_user_password(db=db, user_id=current_user.id, new_password=new_password)
    return {"message": "Password updated successfully"}

