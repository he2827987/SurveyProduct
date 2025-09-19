# backend/app/schemas/answer.py  <-- 文件名改为 answer.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

# 用于接收用户提交的回答
class SurveyAnswerCreate(BaseModel): # <-- 类名改为 SurveyAnswerCreate
    answers: Dict[str, Any] = Field(..., description="A dictionary where keys are question IDs (as strings) and values are the answers.")
    respondent_name: Optional[str] = Field(None, description="Respondent's name")
    department: Optional[str] = Field(None, description="Respondent's department")
    position: Optional[str] = Field(None, description="Respondent's position")
    department_id: Optional[int] = Field(None, description="Department ID")
    organization_id: Optional[int] = Field(None, description="Organization ID")

# 用于返回给客户端的回答数据
class SurveyAnswerInDBBase(BaseModel): # <-- 类名改为 SurveyAnswerInDBBase
    id: int
    survey_id: int
    user_id: Optional[int] = None
    submitted_at: datetime
    answers: Dict[str, Any]

    class Config:
        from_attributes = True

# 用于 API 响应
class SurveyAnswerResponse(SurveyAnswerInDBBase): # <-- 类名改为 SurveyAnswerResponse
    pass

# 用于 __init__.py 导入
class SurveyAnswer(SurveyAnswerInDBBase): # <-- 类名改为 SurveyAnswer
    pass
