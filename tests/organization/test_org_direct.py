#!/usr/bin/env python3
"""
直接测试组织创建
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember
from backend.app.schemas.organization import OrganizationCreate
from backend.app.schemas.organization_member import OrganizationMemberCreate

def test_create_organization_direct():
    """直接测试创建组织"""
    try:
        db = SessionLocal()
        print("数据库连接成功")
        
        # 创建组织数据
        org_data = OrganizationCreate(
            name="测试组织3",
            description="这是第三个测试组织"
        )
        print(f"组织数据: {org_data}")
        
        # 创建组织
        db_org = Organization(
            name=org_data.name,
            description=org_data.description,
            owner_id=3  # admin用户的ID
        )
        print(f"组织对象: {db_org}")
        
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        
        print(f"组织创建成功: {db_org.name} (ID: {db_org.id})")
        
        # 创建组织成员
        member_data = OrganizationMemberCreate(
            organization_id=db_org.id,
            user_id=3,
            role="owner"
        )
        print(f"成员数据: {member_data}")
        
        db_member = OrganizationMember(
            organization_id=member_data.organization_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
        print(f"成员对象: {db_member}")
        
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        
        print(f"成员创建成功: {db_member.role} (ID: {db_member.id})")
        
        db.close()
        return True
    except Exception as e:
        print(f"创建组织失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_create_organization_direct()
