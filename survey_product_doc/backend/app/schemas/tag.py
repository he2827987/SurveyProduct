# backend/app/schemas/tag.py
"""
标签相关的Pydantic模式
定义标签的请求和响应数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagBase(BaseModel):
    """标签基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="标签名称")
    color: Optional[str] = Field("#409EFF", max_length=20, description="标签颜色")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")

class TagCreate(TagBase):
    """创建标签请求模式"""
    pass

class TagUpdate(BaseModel):
    """更新标签请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")

class TagResponse(TagBase):
    """标签响应模式"""
    id: int = Field(..., description="标签ID")
    question_count: int = Field(0, description="关联的题目数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True
