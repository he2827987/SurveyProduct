#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试模块导入"""
    try:
        print("1. 测试导入 department_api...")
        from backend.app.api import department_api
        print("   ✅ department_api 导入成功")
        
        print("2. 测试导入 Department 模型...")
        from backend.app.models.department import Department
        print("   ✅ Department 模型导入成功")
        
        print("3. 测试导入 Department 模式...")
        from backend.app.schemas.department import DepartmentCreate, DepartmentResponse
        print("   ✅ Department 模式导入成功")
        
        print("4. 测试导入 Organization 模型...")
        from backend.app.models.organization import Organization
        print("   ✅ Organization 模型导入成功")
        
        print("5. 测试导入 OrganizationMember 模型...")
        from backend.app.models.organization_member import OrganizationMember
        print("   ✅ OrganizationMember 模型导入成功")
        
        print("6. 测试导入 User 模型...")
        from backend.app.models.user import User
        print("   ✅ User 模型导入成功")
        
        print("7. 测试导入 deps...")
        from backend.app.api import deps
        print("   ✅ deps 导入成功")
        
        print("8. 测试导入 get_db...")
        from backend.app.database import get_db
        print("   ✅ get_db 导入成功")
        
        print("\n所有导入测试通过！")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
