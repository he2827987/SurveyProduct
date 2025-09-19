#!/usr/bin/env python3
import requests
import json
import time

def test_department_with_error_handling():
    """测试部门API并捕获详细错误"""
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
    
    # 测试部门创建
    url = "http://localhost:8000/api/v1/organizations/6/departments"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试数据
    data = {
        "name": "测试部门",
        "code": f"TEST_{int(time.time())}",
        "description": "这是一个测试部门"
    }
    
    print(f"\n2. 测试部门创建...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        # 先测试GET请求
        print("\n2.1. 测试GET请求...")
        get_response = requests.get(url, headers=headers)
        print(f"GET状态码: {get_response.status_code}")
        print(f"GET响应: {get_response.text}")
        
        # 再测试POST请求
        print("\n2.2. 测试POST请求...")
        post_response = requests.post(url, json=data, headers=headers)
        print(f"POST状态码: {post_response.status_code}")
        print(f"POST响应: {post_response.text}")
        
        if post_response.status_code in [200, 201]:
            print(f"成功响应: {post_response.json()}")
        else:
            print(f"错误响应: {post_response.text}")
            try:
                error_json = post_response.json()
                print(f"错误JSON: {json.dumps(error_json, ensure_ascii=False, indent=2)}")
            except:
                print("无法解析错误响应为JSON")
                
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_department_with_error_handling()
