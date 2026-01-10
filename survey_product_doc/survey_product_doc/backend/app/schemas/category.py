# backend/app/schemas/category.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="分类名称")
    description: Optional[str] = Field(None, max_length=1000, description="分类描述")
    code: Optional[str] = Field(None, max_length=50, description="分类编码")
    parent_id: Optional[int] = Field(None, description="上级分类ID")
    sort_order: Optional[int] = Field(0, description="排序字段")
    is_active: Optional[bool] = Field(True, description="是否激活")

class CategoryCreate(CategoryBase):
    """创建分类模型"""
    organization_id: Optional[int] = Field(None, description="组织ID，为空表示全局分类")

class CategoryUpdate(BaseModel):
    """更新分类模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="分类名称")
    description: Optional[str] = Field(None, max_length=1000, description="分类描述")
    code: Optional[str] = Field(None, max_length=50, description="分类编码")
    parent_id: Optional[int] = Field(None, description="上级分类ID")
    sort_order: Optional[int] = Field(None, description="排序字段")
    is_active: Optional[bool] = Field(None, description="是否激活")

class CategoryResponse(CategoryBase):
    """分类响应模型"""
    id: int
    level: int
    path: Optional[str]
    organization_id: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    children: List['CategoryResponse'] = []
    question_count: Optional[int] = Field(0, description="该分类下的题目数量")

    class Config:
        from_attributes = True

# 解决循环引用
CategoryResponse.model_rebuild()

class CategoryTreeResponse(BaseModel):
    """分类树响应模型"""
    id: int
    name: str
    description: Optional[str]
    level: int
    path: Optional[str]
    sort_order: int
    is_active: bool
    question_count: int
    children: List['CategoryTreeResponse'] = []
    
    class Config:
        from_attributes = True

# 解决循环引用
CategoryTreeResponse.model_rebuild()

class CategoryMoveRequest(BaseModel):
    """移动分类请求模型"""
    target_parent_id: Optional[int] = Field(None, description="目标父分类ID，为空表示移动到顶级")
    position: Optional[int] = Field(None, description="在同级中的位置")

class CategoryBulkUpdateRequest(BaseModel):
    """批量更新分类请求模型"""
    category_ids: List[int] = Field(..., description="要更新的分类ID列表")
    parent_id: Optional[int] = Field(None, description="新的父分类ID")
    is_active: Optional[bool] = Field(None, description="是否激活")
