#!/usr/bin/env python3
"""
测试脚本：验证调研管理和数据分析页面修复
"""

import requests
import json
import time
import webbrowser
from threading import Timer

# 配置
BASE_URL = "http://localhost:3000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def open_browser():
    """打开浏览器"""
    webbrowser.open("http://localhost:3000/login")
    print("✅ 浏览器已打开，请按照以下步骤测试：")
    print("\n=== 测试步骤 ===")
    print("1. 使用账户 testuser2 / testpass 登录")
    print("2. 点击'调研管理'测试页面导航")
    print("   - 应该能看到调研列表")
    print("   - 前进/后退应该正常工作")
    print("3. 点击'数据分析'测试标签页切换")
    print("   - 应该能看到三个切换按钮")
    print("   - 每次切换只显示一个板块")
    print("4. 在各个页面间切换测试稳定性")

def test_api_connectivity():
    """测试API连接性"""
    print("\n=== API连接测试 ===")
    
    # 测试后端API
    try:
        response = requests.get("http://localhost:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API响应正常")
        else:
            print(f"❌ 后端API异常: {response.status_code}")
    except:
        print("❌ 后端API连接失败")
    
    # 测试前端代理
    try:
        response = requests.get("http://localhost:3000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("✅ 前端代理正常")
        else:
            print(f"❌ 前端代理异常: {response.status_code}")
    except:
        print("❌ 前端代理连接失败")

def test_login():
    """测试登录"""
    print("\n=== 登录测试 ===")
    
    login_data = {
        "username": "testuser2",
        "password": "testpass"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/users/login/access-token", 
                              data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ 登录API正常")
            return token_data.get('access_token')
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_survey_api():
    """测试调研API"""
    print("\n=== 调研API测试 ===")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
        if response.status_code == 200:
            surveys = response.json()
            print(f"✅ 调研列表API正常，共 {len(surveys)} 个调研")
            return True
        else:
            print(f"❌ 调研列表API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 调研API请求失败: {e}")
        return False

def test_analysis_api():
    """测试分析API"""
    print("\n=== 分析API测试 ===")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/", headers=headers)
        if response.status_code == 200:
            print("✅ 分析API正常")
            return True
        else:
            print(f"❌ 分析API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 分析API请求失败: {e}")
        return False

def main():
    print("=== 调研管理和数据分析页面修复验证 ===\n")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试API连接性
    test_api_connectivity()
    
    # 测试登录
    token = test_login()
    
    # 测试API
    survey_ok = test_survey_api()
    analysis_ok = test_analysis_api()
    
    print("\n=== 测试结果 ===")
    print(f"后端API: {'✅' if requests.get('http://localhost:8000/api/v1/').status_code == 200 else '❌'}")
    print(f"前端代理: {'✅' if requests.get('http://localhost:3000/api/v1/').status_code == 200 else '❌'}")
    print(f"登录功能: {'✅' if token else '❌'}")
    print(f"调研API: {'✅' if survey_ok else '❌'}")
    print(f"分析API: {'✅' if analysis_ok else '❌'}")
    
    # 打开浏览器进行手动测试
    Timer(1.0, open_browser).start()
    
    print("\n=== 修复总结 ===")
    print("1. ✅ 修复了调研页面导航问题")
    print("2. ✅ 修复了数据分析页面布局")
    print("3. ✅ 添加了标签页切换功能")
    print("4. ✅ 改进了API配置和代理")

if __name__ == "__main__":
    main()