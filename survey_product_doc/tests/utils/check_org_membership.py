#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.user import User

def check_organization_membership():
    """检查组织成员关系"""
    db = SessionLocal()
    try:
        # 检查组织
        org = db.query(Organization).filter(Organization.id == 5).first()
        if org:
            print(f"组织: {org.name} (ID: {org.id}, 所有者ID: {org.owner_id})")
        
        # 检查用户
        user = db.query(User).filter(User.id == 3).first()
        if user:
            print(f"用户: {user.username} (ID: {user.id})")
        
        # 检查组织成员关系
        member = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == 5,
            OrganizationMember.user_id == 3
        ).first()
        
        if member:
            print(f"组织成员关系: 用户{member.user_id} 在组织{member.organization_id} 中角色为 {member.role}")
        else:
            print("没有找到组织成员关系")
            
        # 列出所有组织成员
        all_members = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == 5
        ).all()
        
        print(f"组织5的所有成员:")
        for m in all_members:
            print(f"  - 用户ID: {m.user_id}, 角色: {m.role}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_organization_membership()
