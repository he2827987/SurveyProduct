#!/usr/bin/env python3
import requests

def test_simple_endpoints():
    """测试简单的API端点"""
    print("1. 测试根端点...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n2. 测试用户登录...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post("http://localhost:8000/api/v1/users/login/access-token", data=login_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   登录成功")
        else:
            print(f"   登录失败: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n3. 测试组织列表...")
    try:
        response = requests.get("http://localhost:8000/api/v1/organizations/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   获取组织列表成功")
        else:
            print(f"   获取组织列表失败: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    test_simple_endpoints()
