#!/usr/bin/env python3
"""
简单的组织创建测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.organization import Organization
from backend.app.schemas.organization import OrganizationCreate

def test_create_organization():
    """测试创建组织"""
    try:
        db = SessionLocal()
        print("数据库连接成功")
        
        # 创建组织数据
        org_data = OrganizationCreate(
            name="测试组织",
            description="这是一个测试组织"
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
        
        db.close()
        return True
    except Exception as e:
        print(f"创建组织失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_create_organization()
