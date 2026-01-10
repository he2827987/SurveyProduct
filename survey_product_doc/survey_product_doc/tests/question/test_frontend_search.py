#!/usr/bin/env python3
"""
前端搜索功能测试脚本
测试前端搜索参数是否正确传递给后端
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json

def test_frontend_search_params():
    """测试前端搜索参数是否正确传递"""
    base_url = "http://localhost:8000"
    
    print("🔍 前端搜索参数测试")
    print("=" * 50)
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/api/v1/users/login/access-token", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    print()
    
    # 2. 测试前端搜索参数格式
    print("2. 测试前端搜索参数格式...")
    print("-" * 30)
    
    # 模拟前端发送的搜索参数
    frontend_params = {
        "search": "工作环境",  # 搜索关键词
        "type": "single_choice",  # 题目类型
        "skip": 0,  # 分页偏移
        "limit": 10  # 每页数量
    }
    
    print(f"前端发送的参数: {frontend_params}")
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=frontend_params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 后端正确接收参数，返回 {data.get('total', 0)} 个结果")
        print(f"   搜索关键词: {frontend_params['search']}")
        print(f"   题目类型: {frontend_params['type']}")
        print(f"   分页: skip={frontend_params['skip']}, limit={frontend_params['limit']}")
        
        # 显示搜索结果
        if data.get('items'):
            print(f"   搜索结果示例:")
            for i, question in enumerate(data['items'][:3]):
                print(f"     {i+1}. {question['text'][:50]}...")
    else:
        print(f"❌ 后端接收参数失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 3. 测试空搜索参数
    print("3. 测试空搜索参数...")
    print("-" * 30)
    
    empty_params = {
        "search": "",  # 空搜索
        "skip": 0,
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=empty_params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 空搜索参数处理正确，返回 {data.get('total', 0)} 个结果")
    else:
        print(f"❌ 空搜索参数处理失败: {response.status_code}")
    
    print()
    
    # 4. 测试特殊字符搜索
    print("4. 测试特殊字符搜索...")
    print("-" * 30)
    
    special_params = {
        "search": "？",  # 特殊字符
        "skip": 0,
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=special_params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 特殊字符搜索正确，返回 {data.get('total', 0)} 个结果")
    else:
        print(f"❌ 特殊字符搜索失败: {response.status_code}")
    
    print()
    
    # 5. 测试组合参数
    print("5. 测试组合参数...")
    print("-" * 30)
    
    combined_params = {
        "search": "满意度",
        "type": "single_choice",
        "skip": 0,
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=combined_params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 组合参数处理正确，返回 {data.get('total', 0)} 个结果")
        print(f"   搜索: '{combined_params['search']}' + 类型: {combined_params['type']}")
    else:
        print(f"❌ 组合参数处理失败: {response.status_code}")
    
    print()
    print("🎉 前端搜索参数测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_frontend_search_params()
