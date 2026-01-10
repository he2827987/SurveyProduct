# backend/app/models/option.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    
    # 问题ID，外键关联到 questions 表的 id
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # 选项文本
    option_text = Column(Text, nullable=False)
    
    # 选项值 (如果需要，例如 A, B, C 或 1, 2, 3)
    # 可以是可选的，取决于具体需求
    option_value = Column(String(255), nullable=True) 
    
    # 与 Question 模型的关系
    question = relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<Option(id={self.id}, question_id={self.question_id}, option_text='{self.option_text[:30]}...')>"

