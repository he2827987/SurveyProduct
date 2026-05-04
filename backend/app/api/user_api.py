# backend/app/api/user_api.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.token import Token
from app.services import user_service
from app.security import create_access_token
from datetime import timedelta, datetime, timezone
from app.security import create_access_token, get_current_user
from app.config import settings
from app.models.user import User as UserModel
import random
import string

_reset_codes: dict = {}

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取当前登录用户的信息。
    - 需要有效的 JWT 访问令牌。
    """
    # 补充 organization_name 便于前端显示
    if current_user.organization_id:
        try:
            from app import crud
            org = crud.get_organization(db, org_id=current_user.organization_id)  # type: ignore
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


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


@router.post("/forgot-password")
async def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    db_user = user_service.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="该邮箱未注册")

    code = _generate_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_CODE_EXPIRE_MINUTES)
    _reset_codes[email] = {"code": code, "expires": expires}

    from app.services.email_service import send_verification_code_email
    ok = await send_verification_code_email(email, code)
    if not ok:
        raise HTTPException(status_code=500, detail="邮件发送失败，请稍后重试")

    return {"message": "验证码已发送", "detail": f"验证码已发送至 {email}（SMTP未配置时请查看服务端日志获取验证码）"}


@router.post("/verify-reset-code")
async def verify_reset_code(data: dict):
    email = data.get("email")
    code = data.get("code")
    if not email or not code:
        raise HTTPException(status_code=400, detail="邮箱和验证码不能为空")

    entry = _reset_codes.get(email)
    if not entry:
        raise HTTPException(status_code=400, detail="请先发送验证码")

    if datetime.now(timezone.utc) > entry["expires"]:
        _reset_codes.pop(email, None)
        raise HTTPException(status_code=400, detail="验证码已过期，请重新发送")

    if entry["code"] != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    entry["verified"] = True
    return {"message": "验证码验证成功"}


@router.post("/reset-password")
async def reset_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")
    if not email or not code or not new_password:
        raise HTTPException(status_code=400, detail="邮箱、验证码和新密码不能为空")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")

    entry = _reset_codes.get(email)
    if not entry or not entry.get("verified"):
        raise HTTPException(status_code=400, detail="请先完成验证码验证")

    if entry["code"] != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    if datetime.now(timezone.utc) > entry["expires"]:
        _reset_codes.pop(email, None)
        raise HTTPException(status_code=400, detail="验证码已过期，请重新发送")

    updated = user_service.update_user_password_by_email(db=db, email=email, new_password=new_password)
    if not updated:
        raise HTTPException(status_code=404, detail="用户不存在")

    _reset_codes.pop(email, None)
    return {"message": "密码重置成功"}

