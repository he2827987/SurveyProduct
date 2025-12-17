# backend/app/schemas/survey.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 用于创建问卷的请求体
class SurveyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="问卷标题")
    description: Optional[str] = Field(None, description="问卷描述")
    organization_id: Optional[int] = Field(None, description="组织ID")
    question_ids: Optional[list[int]] = Field(None, description="关联的题目ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "用户满意度调查",
                "description": "这是一份关于产品用户满意度的调查问卷。",
                "question_ids": [1, 2, 3]
            }
        }

# 用于更新问卷的请求体
class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="问卷标题")
    description: Optional[str] = Field(None, max_length=1000, description="问卷描述")
    status: Optional[str] = Field(None, description="问卷状态")
    question_ids: Optional[list[int]] = Field(None, description="关联的题目ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "更新后的用户满意度调查",
                "description": "这是一份更新后的关于产品用户满意度的调查问卷。",
                "status": "active"
            }
        }

# 用于返回问卷信息的响应体
class SurveyStatusUpdate(BaseModel):
    status: str = Field(..., description="问卷状态: pending/active/completed")
    end_time: Optional[datetime] = Field(None, description="问卷结束时间")
    start_time: Optional[datetime] = Field(None, description="问卷开始时间")

class SurveyResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: Optional[str] = None
    organization_id: Optional[int] = None
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] # updated_at 可能是 None，直到第一次更新
    questions: Optional[list] = None  # 关联的题目列表（通过中间表获取）
    question_count: int = 0
    response_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True # 兼容 SQLAlchemy 模型
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "用户满意度调查",
                "description": "这是一份关于产品用户满意度的调查问卷。",
                "status": "pending",
                "created_by_user_id": 1,
                "created_at": "2023-10-27T10:00:00.000Z",
                "updated_at": "2023-10-27T10:00:00.000Z",
                "questions": [],
                "answers": []
            }
        }

