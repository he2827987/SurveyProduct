#!/usr/bin/env python3
"""
简单的组织创建测试
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_create_organization():
    """测试创建组织"""
    # 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    token = token_data["access_token"]
    
    # 创建组织
    headers = {"Authorization": f"Bearer {token}"}
    org_data = {
        "name": "测试组织",
        "description": "这是一个测试组织"
    }
    
    response = requests.post(f"{BASE_URL}/organizations/", json=org_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        org = response.json()
        print(f"创建组织成功: {org['name']} (ID: {org['id']})")
        return org["id"]
    else:
        print(f"创建组织失败: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    test_create_organization()
