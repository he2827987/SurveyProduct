#!/usr/bin/env python3
"""
简单的API测试
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """测试API"""
    # 1. 测试登录
    print("1. 测试登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
    print(f"登录状态: {response.status_code}")
    print(f"登录响应: {response.text}")
    
    if response.status_code != 200:
        print("登录失败")
        return
    
    token_data = response.json()
    token = token_data["access_token"]
    print(f"获取到token: {token[:20]}...")
    
    # 2. 测试获取用户信息
    print("\n2. 测试获取用户信息...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"用户信息状态: {response.status_code}")
    print(f"用户信息: {response.text}")
    
    # 3. 测试创建组织
    print("\n3. 测试创建组织...")
    org_data = {
        "name": "测试组织2",
        "description": "这是第二个测试组织"
    }
    
    response = requests.post(f"{BASE_URL}/organizations/", json=org_data, headers=headers)
    print(f"创建组织状态: {response.status_code}")
    print(f"创建组织响应: {response.text}")

if __name__ == "__main__":
    test_api()
