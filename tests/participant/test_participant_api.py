
#!/usr/bin/env python3
import requests
import json
import time

def test_participant_api():
    """测试参与者API"""
    # 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("1. 登录获取token...")
    try:
        login_response = requests.post("http://localhost:8000/api/v1/users/login/access-token", data=login_data)
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print(f"登录成功，token: {token[:20]}...")
    except Exception as e:
        print(f"登录异常: {e}")
        return
    
    # 测试参与者API
    url = "http://localhost:8000/api/v1/organizations/6/participants"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试数据
    data = {
        "name": "测试参与者",
        "position": "测试职位",
        "email": "test@example.com",
        "phone": "13800000000",
        "organization_id": 6
    }
    
    print(f"\n2. 测试参与者API...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        # 测试GET请求
        print("\n2.1. 测试GET请求...")
        get_response = requests.get(url, headers=headers)
        print(f"GET状态码: {get_response.status_code}")
        print(f"GET响应: {get_response.text}")
        
        # 测试POST请求
        print("\n2.2. 测试POST请求...")
        post_response = requests.post(url, json=data, headers=headers)
        print(f"POST状态码: {post_response.status_code}")
        print(f"POST响应: {post_response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")

if __name__ == "__main__":
    test_participant_api()
