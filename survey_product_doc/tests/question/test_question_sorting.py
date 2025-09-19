#!/usr/bin/env python3
"""
题目排序功能测试脚本
测试题目的各种排序方式
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json

def test_question_sorting():
    """测试题目排序功能"""
    base_url = "http://localhost:8000"
    
    print("📊 题目排序功能测试")
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
    
    # 2. 测试创建时间降序排序
    print("2. 测试创建时间降序排序...")
    print("-" * 30)
    
    params = {
        "sort_by": "created_desc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 创建时间降序排序成功，返回 {len(data.get('items', []))} 个题目")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}...")
    else:
        print(f"❌ 创建时间降序排序失败: {response.status_code}")
    
    print()
    
    # 3. 测试创建时间升序排序
    print("3. 测试创建时间升序排序...")
    print("-" * 30)
    
    params = {
        "sort_by": "created_asc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 创建时间升序排序成功，返回 {len(data.get('items', []))} 个题目")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}...")
    else:
        print(f"❌ 创建时间升序排序失败: {response.status_code}")
    
    print()
    
    # 4. 测试使用次数降序排序
    print("4. 测试使用次数降序排序...")
    print("-" * 30)
    
    params = {
        "sort_by": "usage_desc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 使用次数降序排序成功，返回 {len(data.get('items', []))} 个题目")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}... (使用次数: {question.get('usage_count', 0)})")
    else:
        print(f"❌ 使用次数降序排序失败: {response.status_code}")
    
    print()
    
    # 5. 测试使用次数升序排序
    print("5. 测试使用次数升序排序...")
    print("-" * 30)
    
    params = {
        "sort_by": "usage_asc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 使用次数升序排序成功，返回 {len(data.get('items', []))} 个题目")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}... (使用次数: {question.get('usage_count', 0)})")
    else:
        print(f"❌ 使用次数升序排序失败: {response.status_code}")
    
    print()
    
    # 6. 测试组合排序（搜索+排序）
    print("6. 测试组合排序（搜索+排序）...")
    print("-" * 30)
    
    params = {
        "search": "工作环境",
        "sort_by": "usage_desc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 组合排序成功，返回 {len(data.get('items', []))} 个包含'工作环境'的题目（按使用次数降序）")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}... (使用次数: {question.get('usage_count', 0)})")
    else:
        print(f"❌ 组合排序失败: {response.status_code}")
    
    print()
    
    # 7. 测试类型筛选+排序
    print("7. 测试类型筛选+排序...")
    print("-" * 30)
    
    params = {
        "type": "single_choice",
        "sort_by": "usage_asc",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 类型筛选+排序成功，返回 {len(data.get('items', []))} 个单选题（按使用次数升序）")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}... (类型: {question['type']}, 使用次数: {question.get('usage_count', 0)})")
    else:
        print(f"❌ 类型筛选+排序失败: {response.status_code}")
    
    print()
    
    # 8. 测试无排序参数（默认排序）
    print("8. 测试无排序参数（默认排序）...")
    print("-" * 30)
    
    params = {
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 默认排序成功，返回 {len(data.get('items', []))} 个题目")
        for i, question in enumerate(data.get('items', [])[:3]):
            print(f"   {i+1}. ID {question['id']}: {question['text'][:50]}...")
    else:
        print(f"❌ 默认排序失败: {response.status_code}")
    
    print()
    print("🎉 题目排序功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_question_sorting()
