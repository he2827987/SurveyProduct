#!/usr/bin/env python3
"""
简单的登录测试
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录获取token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token: {token_data}")
        return token_data["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    test_login()
