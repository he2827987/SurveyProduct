# backend/app/models_updated.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum
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
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    # 定义与 Survey 和 Answer 的关系
    surveys = relationship("Survey", foreign_keys="Survey.created_by_user_id", back_populates="creator")
    answers = relationship("Answer", back_populates="user")
    
    # 新增关系
    questions_owned = relationship("Question", back_populates="owner")
    organization = relationship("Organization", foreign_keys=[organization_id], back_populates="members")
    manager = relationship("User", remote_side=[id], backref="subordinates")

# 组织模型
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, nullable=True)
    is_public = Column(Boolean, nullable=True)

    # 定义关系
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_organizations")
    members = relationship("User", foreign_keys=[User.organization_id], back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    categories = relationship("Category", back_populates="organization")
    questions = relationship("Question", back_populates="organization")
    surveys = relationship("Survey", back_populates="organization")
    participants = relationship("Participant", back_populates="organization")

# 组织成员模型
class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

# 部门模型
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    level = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 定义关系
    organization = relationship("Organization", back_populates="departments")
    parent = relationship("Department", remote_side=[id], backref="children")
    participants = relationship("Participant", back_populates="department")

# 分类模型
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, nullable=True)
    path = Column(String(500), nullable=True)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 定义关系
    organization = relationship("Organization", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    creator = relationship("User", foreign_keys=[created_by])
    questions = relationship("Question", back_populates="category")

# 标签模型
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(20), default='#409EFF')
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 定义与 Question 的多对多关系
    questions = relationship("Question", secondary="question_tags", back_populates="tags")

# 问题模型
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    type = Column(Enum('SINGLE_CHOICE', 'MULTI_CHOICE', 'TEXT_INPUT', 'NUMBER_INPUT', name='question_type'), nullable=False)
    options = Column(Text, nullable=True)  # JSON格式存储选项
    is_required = Column(Boolean, nullable=True)
    order = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    min_score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)

    # 定义关系
    owner = relationship("User", back_populates="questions_owned")
    organization = relationship("Organization", back_populates="questions")
    category = relationship("Category", back_populates="questions")
    tags = relationship("Tag", secondary="question_tags", back_populates="questions")
    
    # 定义与 Answer 的关系
    answers = relationship("Answer", back_populates="question")
    
    # 定义与 SurveyQuestion 的关系
    survey_questions = relationship("SurveyQuestion", back_populates="question")

# 题目标签关联表（多对多关系）
class QuestionTag(Base):
    __tablename__ = "question_tags"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

# 问卷模型
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    status = Column(String(50), nullable=False)

    # 定义与 User 的关系
    creator = relationship("User", foreign_keys=[created_by_user_id], back_populates="surveys")
    organization = relationship("Organization", back_populates="surveys")
    
    # 定义与 SurveyQuestion 的关系
    survey_questions = relationship("SurveyQuestion", back_populates="survey")
    
    # 定义与 Answer 的关系
    answers = relationship("Answer", back_populates="survey")

# 问卷题目关联表
class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True)

    # 定义关系
    survey = relationship("Survey", back_populates="survey_questions")
    question = relationship("Question", back_populates="survey_questions")

# 参与者模型
class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    position = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 定义关系
    department = relationship("Department", back_populates="participants")
    organization = relationship("Organization", back_populates="participants")
    
    # 定义与 Answer 的关系
    answers = relationship("Answer", back_populates="participant")

# 答案模型
class Answer(Base):
    __tablename__ = "survey_answers"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    answers = Column(Text, nullable=False)  # JSON格式存储答案
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    total_score = Column(Integer, nullable=True)
    department = Column(Text, nullable=True)
    position = Column(Text, nullable=True)

    # 定义关系
    survey = relationship("Survey", back_populates="answers")
    user = relationship("User", back_populates="answers")
    participant = relationship("Participant", back_populates="answers")
