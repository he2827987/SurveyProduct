#!/usr/bin/env python3
import requests
import json

def test_create_department_simple():
    """简单测试部门创建"""
    # 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post("http://localhost:8000/api/v1/users/login/access-token", data=login_data)
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code} - {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"登录成功，获取到token: {token[:20]}...")
    
    url = "http://localhost:8000/api/v1/organizations/5/departments"
    
    import time
    # 测试数据
    data = {
        "name": "研发部",
        "code": f"RD_{int(time.time())}",
        "description": "负责产品研发"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("测试创建部门（简单测试）...")
    print(f"URL: {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            print(f"成功响应: {response.json()}")
        else:
            print(f"错误响应: {response.text}")
            try:
                error_json = response.json()
                print(f"错误JSON: {json.dumps(error_json, ensure_ascii=False, indent=2)}")
            except:
                print("无法解析错误响应为JSON")
                
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")

if __name__ == "__main__":
    test_create_department_simple()
