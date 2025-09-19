# backend/app/schemas/participant.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="参与者姓名")
    department_id: Optional[int] = Field(None, description="所属部门ID")
    position: Optional[str] = Field(None, max_length=255, description="职位")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="电话")

class ParticipantCreate(ParticipantBase):
    organization_id: int = Field(..., description="组织ID")

class ParticipantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="参与者姓名")
    department_id: Optional[int] = Field(None, description="所属部门ID")
    position: Optional[str] = Field(None, max_length=255, description="职位")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="电话")

class ParticipantResponse(ParticipantBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
