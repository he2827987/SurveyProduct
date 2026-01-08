# backend/app/schemas/department.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="部门名称")
    code: Optional[str] = Field(None, max_length=50, description="部门编码")
    description: Optional[str] = Field(None, description="部门描述")
    parent_id: Optional[int] = Field(None, description="上级部门ID")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="部门名称")
    code: Optional[str] = Field(None, max_length=50, description="部门编码")
    description: Optional[str] = Field(None, description="部门描述")
    parent_id: Optional[int] = Field(None, description="上级部门ID")

class DepartmentResponse(DepartmentBase):
    id: int
    organization_id: int
    level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    children: Optional[List['DepartmentResponse']] = []

    class Config:
        from_attributes = True

# 解决循环引用
DepartmentResponse.model_rebuild()
