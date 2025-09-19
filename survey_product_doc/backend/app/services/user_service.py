# backend/app/services/user_service.py

from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from passlib.context import CryptContext # 用于密码哈希

# 初始化密码哈希上下文
# 使用 bcrypt 算法，这是目前推荐的密码哈希算法之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    对密码进行哈希处理
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str) -> User | None:
    """
    根据用户名获取用户
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    根据邮箱获取用户
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role # 默认是 'employee'，但允许通过 UserCreate 指定
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # 刷新 db_user 以获取数据库生成的数据（如 id, created_at）
    return db_user

def update_user(db: Session, user_id: int, user_update) -> User:
    """
    更新用户信息
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "password":  # 密码单独处理
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str) -> User:
    """
    更新用户密码
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    # 对新密码进行哈希处理
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    
    db.commit()
    db.refresh(db_user)
    return db_user

