#!/usr/bin/env python3
import requests
import json

def test_department_no_auth():
    """测试部门API（不需要认证）"""
    url = "http://localhost:8000/api/v1/organizations/5/departments"
    
    # 测试数据
    data = {
        "name": "研发部",
        "code": "RD_TEST",
        "description": "负责产品研发"
    }
    
    print("测试创建部门（不需要认证）...")
    print(f"URL: {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
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
    test_department_no_auth()
