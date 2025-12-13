# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# 用于用户注册请求体
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "employee" # 默认是员工

# 用于用户登录请求体
class UserLogin(BaseModel):
    username: str
    password: str

# 用于用户更新请求体 (所有字段可选)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6) # 更新密码时使用
    role: Optional[str] = None
    organization_id: Optional[int] = None # 允许更新所属组织

# 用于用户响应体（返回给前端的用户信息）
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime
    organization_id: Optional[int] = None # 用户可能暂时没有组织
    organization_name: Optional[str] = None

    class Config:
        from_attributes = True # 兼容 SQLAlchemy ORM 对象

# 用于组织响应体（在用户响应中可能需要包含组织信息）
class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

