# backend/app/models/department.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class Department(Base):
    """
    部门模型
    支持组织的层级部门结构
    """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 部门名称
    code = Column(String(50), nullable=True)    # 部门编码
    description = Column(Text, nullable=True)   # 部门描述
    
    # 组织关联
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="departments")
    
    # 上级部门（自关联）
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    parent = relationship("Department", remote_side=[id], back_populates="children")
    children = relationship("Department", back_populates="parent")
    
    # 部门层级
    level = Column(Integer, default=1)  # 部门层级，1为顶级部门
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', org_id={self.organization_id})>"
