# backend/app/models/answer.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base
from typing import Optional

class SurveyAnswer(Base):
    __tablename__ = "survey_answers"
    id = Column(Integer, primary_key=True, index=True)
    # 关联到哪个问卷
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    # 关联到哪个用户（如果用户是登录状态）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # 关联到哪个参与者（如果是扫码参与）
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    # 回答提交时间
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    # 存储回答的具体内容，通常是 JSON 格式
    answers = Column(Text, nullable=False) # 存储 JSON 字符串
    
    # 存储回答的总分
    total_score = Column(Integer, default=0)
    
    # 存储受访者部门（直接存储字符串）
    department = Column(Text, nullable=True)
    # 存储受访者职位/等级（直接存储字符串）
    position = Column(Text, nullable=True)

    # 记录所属组织
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization_name = Column(Text, nullable=True)

    # 关系
    survey = relationship("Survey", back_populates="answers")
    user = relationship("User", back_populates="answers")
    participant = relationship("Participant", back_populates="answers")
    organization = relationship("Organization", backref="survey_answers")
