#!/usr/bin/env python3
"""
不需要认证的组织创建测试
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_create_organization_no_auth():
    """测试创建组织（不需要认证）"""
    print("测试创建组织（不需要认证）...")
    
    org_data = {
        "name": "测试组织4",
        "description": "这是第四个测试组织"
    }
    
    response = requests.post(f"{BASE_URL}/organizations/", json=org_data)
    print(f"创建组织状态: {response.status_code}")
    print(f"创建组织响应: {response.text}")

if __name__ == "__main__":
    test_create_organization_no_auth()
