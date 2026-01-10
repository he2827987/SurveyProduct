#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.organization_member import OrganizationMember

def test_department_direct():
    """直接测试部门相关操作"""
    db = SessionLocal()
    try:
        print("1. 检查组织6是否存在...")
        org = db.query(Organization).filter(Organization.id == 6).first()
        if org:
            print(f"   找到组织: {org.name} (ID: {org.id}, 所有者ID: {org.owner_id})")
        else:
            print("   组织6不存在")
            return
        
        print("\n2. 检查用户3是否存在...")
        user = db.query(User).filter(User.id == 3).first()
        if user:
            print(f"   找到用户: {user.username} (ID: {user.id})")
        else:
            print("   用户3不存在")
            return
        
        print("\n3. 检查组织成员关系...")
        member = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == 6,
            OrganizationMember.user_id == 3
        ).first()
        
        if member:
            print(f"   找到成员关系: 用户{member.user_id} 在组织{member.organization_id} 中角色为 {member.role}")
        else:
            print("   没有找到组织成员关系")
        
        print("\n4. 检查现有部门...")
        existing_depts = db.query(Department).filter(Department.organization_id == 6).all()
        print(f"   组织6现有部门数量: {len(existing_depts)}")
        for dept in existing_depts:
            print(f"     - {dept.name} (ID: {dept.id}, 编码: {dept.code})")
        
        print("\n5. 测试创建部门...")
        new_dept = Department(
            name="直接测试部门",
            code="DIRECT_TEST",
            description="直接测试创建的部门",
            organization_id=6,
            level=1
        )
        
        db.add(new_dept)
        db.commit()
        db.refresh(new_dept)
        
        print(f"   部门创建成功: {new_dept.name} (ID: {new_dept.id})")
        
        print("\n6. 验证权限检查函数...")
        # 测试权限检查逻辑
        org_check = db.query(Organization).filter(Organization.id == 6).first()
        if org_check and org_check.owner_id == 3:
            print("   ✅ 用户3是组织6的所有者")
        else:
            print("   ❌ 用户3不是组织6的所有者")
        
        member_check = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == 6,
            OrganizationMember.user_id == 3,
            OrganizationMember.role.in_(["owner", "admin"])
        ).first()
        
        if member_check:
            print(f"   ✅ 用户3有管理权限，角色: {member_check.role}")
        else:
            print("   ❌ 用户3没有管理权限")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_department_direct()
