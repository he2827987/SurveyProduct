# backend/app/models/organization_member.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint # 导入 UniqueConstraint

from backend.app.database import Base

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member", nullable=False) # 例如: "owner", "admin", "member", "viewer"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 定义关系
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")

    # 确保一个用户在一个组织中只能有一个角色
    __table_args__ = (UniqueConstraint('organization_id', 'user_id', name='_organization_user_uc'),)

    def __repr__(self):
        return f"<OrganizationMember(id={self.id}, org_id={self.organization_id}, user_id={self.user_id}, role='{self.role}')>"

