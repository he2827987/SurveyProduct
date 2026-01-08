#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.user import User

def has_organization_manage_access(db, user, org_id):
    """检查用户是否有权限管理组织"""
    # 组织所有者
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org and org.owner_id == user.id:
        print(f"用户{user.id}是组织{org_id}的所有者")
        return True
    
    # 组织管理员
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user.id,
        OrganizationMember.role.in_(["owner", "admin"])
    ).first()
    
    if member:
        print(f"用户{user.id}是组织{org_id}的{member.role}")
        return True
    
    print(f"用户{user.id}没有组织{org_id}的管理权限")
    return False

def test_permission():
    """测试权限检查"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 3).first()
        if not user:
            print("用户不存在")
            return
        
        print(f"测试用户: {user.username} (ID: {user.id})")
        
        # 测试组织5的权限
        has_access = has_organization_manage_access(db, user, 5)
        print(f"对组织5的管理权限: {has_access}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_permission()
