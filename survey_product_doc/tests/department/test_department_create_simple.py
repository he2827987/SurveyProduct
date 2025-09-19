#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.organization_member import OrganizationMember

def test_department_create_simple():
    """简单测试部门创建"""
    db = SessionLocal()
    try:
        print("1. 检查组织6是否存在...")
        org = db.query(Organization).filter(Organization.id == 6).first()
        if not org:
            print("组织6不存在")
            return
        print(f"找到组织: {org.name}")
        
        print("\n2. 检查用户3是否存在...")
        user = db.query(User).filter(User.id == 3).first()
        if not user:
            print("用户3不存在")
            return
        print(f"找到用户: {user.username}")
        
        print("\n3. 检查权限...")
        member = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == 6,
            OrganizationMember.user_id == 3
        ).first()
        if member:
            print(f"用户有权限，角色: {member.role}")
        else:
            print("用户没有权限")
            return
        
        print("\n4. 创建部门...")
        new_dept = Department(
            name="简单测试部门",
            code="SIMPLE_TEST",
            description="简单测试创建的部门",
            organization_id=6,
            level=1
        )
        
        db.add(new_dept)
        db.commit()
        db.refresh(new_dept)
        
        print(f"部门创建成功: {new_dept.name} (ID: {new_dept.id})")
        print(f"created_at: {new_dept.created_at}")
        print(f"updated_at: {new_dept.updated_at}")
        
        # 检查是否能正确序列化
        print("\n5. 测试序列化...")
        dept_dict = {
            "id": new_dept.id,
            "name": new_dept.name,
            "code": new_dept.code,
            "description": new_dept.description,
            "organization_id": new_dept.organization_id,
            "level": new_dept.level,
            "is_active": new_dept.is_active,
            "created_at": new_dept.created_at,
            "updated_at": new_dept.updated_at,
            "parent_id": new_dept.parent_id,
            "children": []
        }
        print(f"序列化成功: {dept_dict}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_department_create_simple()
