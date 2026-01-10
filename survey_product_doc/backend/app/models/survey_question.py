# backend/app/models/survey_question.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base
import datetime

class SurveyQuestion(Base):
    """调研题目关联表"""
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 外键关联
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # 题目在调研中的排序
    order = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    # 关系定义
    survey = relationship("Survey", back_populates="survey_questions")
    question = relationship("Question", back_populates="survey_questions")
    
    def __repr__(self):
        return f"<SurveyQuestion(survey_id={self.survey_id}, question_id={self.question_id}, order={self.order})>"

