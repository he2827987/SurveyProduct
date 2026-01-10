#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.department import Department
from backend.app.models.organization import Organization

def test_department_creation():
    """直接测试部门创建"""
    db = SessionLocal()
    try:
        # 检查组织是否存在
        org = db.query(Organization).filter(Organization.id == 5).first()
        if not org:
            print("组织ID 5不存在")
            return
        
        print(f"找到组织: {org.name}")
        
        # 创建部门
        new_department = Department(
            name="测试部门",
            code="TEST001",
            description="这是一个测试部门",
            organization_id=5,
            level=1
        )
        
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        
        print(f"部门创建成功: {new_department.name} (ID: {new_department.id})")
        
    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_department_creation()
