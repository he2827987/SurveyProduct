# backend/app/models/participant.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class Participant(Base):
    """
    调研参与者模型
    用于存储扫码参与调研的人员信息
    """
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 参与者姓名
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)  # 所属部门
    position = Column(String(255), nullable=True)  # 职位
    email = Column(String(255), nullable=True)  # 邮箱（可选）
    phone = Column(String(50), nullable=True)  # 电话（可选）
    
    # 组织关联
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="participants")
    
    # 部门关联
    department = relationship("Department")
    
    # 答案关联
    answers = relationship("SurveyAnswer", back_populates="participant")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Participant(id={self.id}, name='{self.name}', org_id={self.organization_id})>"
