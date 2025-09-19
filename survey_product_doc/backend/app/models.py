# backend/app/models.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# 从 database.py 导入 Base 对象
from backend.app.database import Base

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # 定义与 Survey 和 Answer 的关系
    surveys = relationship("Survey", back_populates="owner")
    answers = relationship("Answer", back_populates="user")

# 问卷模型
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 外键，关联到 User
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="surveys")

    # 定义与 Question 的关系
    questions = relationship("Question", back_populates="survey")

# 问题模型
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False) # 例如: 'text', 'multiple_choice', 'rating'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键，关联到 Survey
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    survey = relationship("Survey", back_populates="questions")

    # 定义与 Answer 的关系
    answers = relationship("Answer", back_populates="question")

# 答案模型
class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    response = Column(Text, nullable=False) # 用户的回答内容
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键，关联到 User 和 Question
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="answers")

    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="answers")

# 组织模型 (如果需要，可以扩展)
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 可以添加与用户或问卷的关系，例如一个组织可以有多个用户
    # users = relationship("User", back_populates="organization") # 如果 User 模型中添加了 organization_id
