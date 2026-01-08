#!/usr/bin/env python3
import requests
import json

def test_create_organization_detailed():
    """详细测试组织创建API"""
    url = "http://localhost:8000/api/v1/organizations/"
    
    # 测试数据
    data = {
        "name": "测试组织",
        "description": "这是一个测试组织"
    }
    
    print("测试创建组织（详细错误信息）...")
    print(f"URL: {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
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
    test_create_organization_detailed()
