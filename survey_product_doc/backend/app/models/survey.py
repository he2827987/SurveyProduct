# backend/app/models/survey.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base
import datetime

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, active, completed

    # 外键关联到 User 模型，表示问卷的创建者
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="surveys") # 定义与 User 模型的关系

    # 外键关联到 Organization 模型 (如果问卷属于某个组织)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="surveys")

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    # 定义与 SurveyQuestion 模型的关系 (一个问卷可以有多个问题)
    survey_questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan")

    # 定义与 SurveyAnswer 模型的关系 (一个问卷可以有多个回答)
    answers = relationship("SurveyAnswer", back_populates="survey", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Survey(id={self.id}, title='{self.title}', created_by_user_id={self.created_by_user_id})>"

