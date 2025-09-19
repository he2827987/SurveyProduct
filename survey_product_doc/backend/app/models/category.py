# backend/app/models/category.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class Category(Base):
    """
    题目分类模型
    支持多级树状分类结构
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 分类名称
    description = Column(Text, nullable=True)   # 分类描述
    code = Column(String(50), nullable=True)    # 分类编码
    
    # 组织关联（可为空，表示全局分类）
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="categories")
    
    # 上级分类（自关联，支持树状结构）
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    
    # 分类层级
    level = Column(Integer, default=1)  # 分类层级，1为顶级分类
    path = Column(String(500), nullable=True)  # 分类路径，如 "1/3/5"
    
    # 排序
    sort_order = Column(Integer, default=0)  # 排序字段
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', org_id={self.organization_id})>"
