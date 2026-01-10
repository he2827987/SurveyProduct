# backend/app/models/user.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="researcher", nullable=False)  # researcher: 调研发起人
    is_active = Column(Boolean, default=True)  # 用户是否活跃
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    # --- 修正自关联关系 ---
    # 使用 manager/subordinates 模型，更清晰
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager = relationship("User", remote_side=[id], back_populates="subordinates")
    subordinates = relationship("User", back_populates="manager")

    # --- 修正与 Organization 的关系，明确指定 foreign_keys ---
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    # 其他关系保持不变
    organization_memberships = relationship("OrganizationMember", back_populates="user")

    questions = relationship("Question", back_populates="owner", cascade="all, delete-orphan")
    surveys = relationship("Survey", back_populates="owner")
    answers = relationship("SurveyAnswer", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

