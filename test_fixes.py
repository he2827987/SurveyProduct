#!/usr/bin/env python3
"""
测试脚本：验证调研管理和数据分析页面修复
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:3000/api/v1"  # 通过前端代理访问
HEADERS = {
    "Content-Type": "application/json"
}

def test_login():
    """测试登录功能"""
    print("测试登录功能...")
    login_data = {
        "username": "testuser2",
        "password": "testpass"
    }
    
    # 直接访问后端API获取token
    response = requests.post(f"http://localhost:8000/api/v1/users/login/access-token", 
                           data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ 登录成功")
        print(f"   Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_survey_api():
    """测试调研API通过前端代理"""
    print("\n测试调研API（通过前端代理）...")
    
    # 使用固定token测试
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
    
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ 调研列表API通过代理成功")
        for survey in surveys:
            print(f"   - {survey['title']} (ID: {survey['id']}, 状态: {survey['status']})")
        return True
    else:
        print(f"❌ 调研列表API失败: {response.status_code} - {response.text}")
        return False

def test_global_surveys():
    """测试全局调研API"""
    print("\n测试全局调研API...")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/surveys/global/all", headers=headers)
    
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ 全局调研API成功，共 {len(surveys)} 个调研")
        return True
    else:
        print(f"❌ 全局调研API失败: {response.status_code} - {response.text}")
        return False

def test_analysis_base():
    """测试分析基础API"""
    print("\n测试分析基础API...")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/analytics/", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ 分析基础API成功")
        return True
    else:
        print(f"❌ 分析基础API失败: {response.status_code} - {response.text}")
        return False

def test_survey_stats():
    """测试调研统计API"""
    print("\n测试调研统计API...")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/analytics/surveys/37/statistics", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 调研统计API成功")
        print(f"   调研: {stats.get('survey_title', 'N/A')}")
        print(f"   题目数: {stats.get('question_count', 0)}")
        print(f"   答案数: {stats.get('answer_count', 0)}")
        return True
    else:
        print(f"❌ 调研统计API失败: {response.status_code} - {response.text}")
        return False

def test_backend_direct():
    """直接测试后端API"""
    print("\n测试后端API（直接访问）...")
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"http://localhost:8000/api/v1/analytics/", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ 后端直接访问成功")
        return True
    else:
        print(f"❌ 后端直接访问失败: {response.status_code} - {response.text}")
        return False

def main():
    print("=== 调研管理和数据分析页面修复验证 ===\n")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试登录
    token = test_login()
    
    # 测试API
    survey_ok = test_survey_api()
    global_ok = test_global_surveys()
    analysis_ok = test_analysis_base()
    stats_ok = test_survey_stats()
    backend_ok = test_backend_direct()
    
    print(f"\n=== 测试结果 ===")
    print(f"登录: ✅" if token else "❌")
    print(f"调研列表API（通过代理）: {'✅' if survey_ok else '❌'}")
    print(f"全局调研API: {'✅' if global_ok else '❌'}")
    print(f"分析基础API: {'✅' if analysis_ok else '❌'}")
    print(f"调研统计API: {'✅' if stats_ok else '❌'}")
    print(f"后端直接访问: {'✅' if backend_ok else '❌'}")
    
    if survey_ok and analysis_ok and stats_ok:
        print("\n🎉 核心API测试通过！")
        print("\n使用说明：")
        print("1. 访问 http://localhost:3000/login")
        print("2. 使用账户 testuser2 / testpass 登录")
        print("3. 点击左侧菜单的'调研管理'查看调研列表")
        print("4. 点击左侧菜单的'数据分析'查看数据分析")
        print("5. 现在应该能看到正常的数据，不再有错误消息")
    else:
        print("\n⚠️ 部分测试失败")
        print("请检查服务是否正常启动")
        print("后端: http://localhost:8000")
        print("前端: http://localhost:3000")

if __name__ == "__main__":
    main()