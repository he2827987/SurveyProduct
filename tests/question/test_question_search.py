#!/usr/bin/env python3
"""
题目搜索功能测试脚本
测试题目的搜索、筛选功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json

def test_question_search():
    """测试题目搜索功能"""
    base_url = "http://localhost:8000"
    
    print("🔍 题目搜索功能测试")
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
    
    # 2. 测试基础搜索功能
    print("2. 测试基础搜索功能...")
    print("-" * 30)
    
    # 搜索包含"工作环境"的题目
    search_params = {
        "search": "工作环境",
        "limit": 10
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=search_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 搜索'工作环境'成功，找到 {data.get('total', 0)} 个题目")
        for question in data.get('items', [])[:3]:
            print(f"   - {question['text'][:50]}...")
    else:
        print(f"❌ 搜索失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 3. 测试类型筛选
    print("3. 测试类型筛选...")
    print("-" * 30)
    
    # 搜索单选题
    type_params = {
        "type": "single_choice",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=type_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 筛选单选题成功，找到 {data.get('total', 0)} 个单选题")
        for question in data.get('items', [])[:3]:
            print(f"   - {question['text'][:50]}... (类型: {question['type']})")
    else:
        print(f"❌ 类型筛选失败: {response.status_code}")
    
    print()
    
    # 4. 测试组合搜索（搜索+类型筛选）
    print("4. 测试组合搜索（搜索+类型筛选）...")
    print("-" * 30)
    
    # 搜索包含"满意度"的单选题
    combined_params = {
        "search": "满意度",
        "type": "single_choice",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=combined_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 组合搜索成功，找到 {data.get('total', 0)} 个包含'满意度'的单选题")
        for question in data.get('items', [])[:3]:
            print(f"   - {question['text'][:50]}... (类型: {question['type']})")
    else:
        print(f"❌ 组合搜索失败: {response.status_code}")
    
    print()
    
    # 5. 测试分页功能
    print("5. 测试分页功能...")
    print("-" * 30)
    
    # 获取第一页
    page1_params = {
        "skip": 0,
        "limit": 3
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=page1_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 第一页获取成功，共 {data.get('total', 0)} 个题目，当前页 {len(data.get('items', []))} 个")
        print(f"   分页信息: 第{data.get('page', 0)}页，共{data.get('pages', 0)}页")
        
        # 获取第二页
        page2_params = {
            "skip": 3,
            "limit": 3
        }
        
        response2 = requests.get(f"{base_url}/api/v1/questions/", 
                               headers=headers, params=page2_params)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ 第二页获取成功，当前页 {len(data2.get('items', []))} 个题目")
            print(f"   分页信息: 第{data2.get('page', 0)}页，共{data2.get('pages', 0)}页")
        else:
            print(f"❌ 第二页获取失败: {response2.status_code}")
    else:
        print(f"❌ 分页测试失败: {response.status_code}")
    
    print()
    
    # 6. 测试空搜索
    print("6. 测试空搜索...")
    print("-" * 30)
    
    # 搜索不存在的关键词
    empty_params = {
        "search": "不存在的关键词12345",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=empty_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 空搜索测试成功，找到 {data.get('total', 0)} 个题目")
        if data.get('total', 0) == 0:
            print("   ✅ 正确返回空结果")
        else:
            print("   ⚠️  意外返回了结果")
    else:
        print(f"❌ 空搜索测试失败: {response.status_code}")
    
    print()
    
    # 7. 测试特殊字符搜索
    print("7. 测试特殊字符搜索...")
    print("-" * 30)
    
    # 搜索包含特殊字符的题目
    special_params = {
        "search": "？",
        "limit": 5
    }
    
    response = requests.get(f"{base_url}/api/v1/questions/", 
                          headers=headers, params=special_params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 特殊字符搜索成功，找到 {data.get('total', 0)} 个包含'？'的题目")
        for question in data.get('items', [])[:3]:
            print(f"   - {question['text'][:50]}...")
    else:
        print(f"❌ 特殊字符搜索失败: {response.status_code}")
    
    print()
    print("🎉 题目搜索功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_question_search()
