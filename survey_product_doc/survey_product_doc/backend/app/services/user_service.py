# backend/app/services/user_service.py

from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.department import Department
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

    # --- 自动创建默认组织 ---
    # 每个用户注册时，自动创建一个以其用户名命名的组织
    try:
        org_name = f"{user.username}的组织"
        # 确保组织名称唯一（简单处理，如果有重复则添加随机后缀）
        existing_org = db.query(Organization).filter(Organization.name == org_name).first()
        if existing_org:
            import time
            org_name = f"{org_name}_{int(time.time())}"
        
        new_org = Organization(
            name=org_name,
            description=f"由 {user.username} 创建的默认组织",
            owner_id=db_user.id,
            is_active=True
        )
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        # 将用户关联到该组织
        db_user.organization_id = new_org.id
        db.add(db_user)
        
        # 将用户添加为组织成员（管理员/所有者）
        # 注意：这里需要根据 OrganizationMember 模型定义来设置字段
        # 假设 OrganizationMember 有 user_id, organization_id, role, status 等字段
        # 暂时只设置基本字段，具体根据 OrganizationMember 模型调整
        member = OrganizationMember(
            user_id=db_user.id,
            organization_id=new_org.id,
            role="owner"
        )
        db.add(member)
        
        # 自动创建根部门 "总公司"
        root_dept = Department(
            name="总公司",
            code="HQ",
            organization_id=new_org.id,
            parent_id=None,
            level=1,
            description="默认生成的总公司部门"
        )
        db.add(root_dept)
        
        db.commit()
        db.refresh(db_user)
        
    except Exception as e:
        print(f"Error creating default organization for user {db_user.id}: {e}")
        # 不因为组织创建失败而回滚用户创建，但记录错误
        # 或者可以选择回滚：db.rollback(); raise e

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

