#!/usr/bin/env python3
"""
测试脚本：验证调研管理页面修复
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
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
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", 
                           data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ 登录成功")
        print(f"   Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_survey_list(token):
    """测试调研列表"""
    print("\n测试调研列表...")
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
    
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ 调研列表获取成功")
        for survey in surveys:
            print(f"   - {survey['title']} (ID: {survey['id']}, 状态: {survey['status']})")
        return True
    else:
        print(f"❌ 调研列表获取失败: {response.status_code} - {response.text}")
        return False

def test_survey_questions(token):
    """测试调研题目"""
    print("\n测试调研题目...")
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/surveys/37/questions", headers=headers)
    
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ 调研题目获取成功，共 {len(questions)} 个题目")
        for question in questions:
            print(f"   - {question['text'][:50]}...")
        return True
    else:
        print(f"❌ 调研题目获取失败: {response.status_code} - {response.text}")
        return False

def main():
    print("=== 调研管理页面功能测试 ===\n")
    
    # 测试登录
    token = test_login()
    if not token:
        print("登录失败，无法继续测试")
        return
    
    # 测试调研列表
    survey_list_ok = test_survey_list(token)
    
    # 测试调研题目
    questions_ok = test_survey_questions(token)
    
    print(f"\n=== 测试结果 ===")
    print(f"登录: ✅")
    print(f"调研列表: {'✅' if survey_list_ok else '❌'}")
    print(f"调研题目: {'✅' if questions_ok else '❌'}")
    
    if survey_list_ok and questions_ok:
        print("\n🎉 所有测试通过！")
        print("\n使用说明：")
        print("1. 访问 http://127.0.0.1:8000/login")
        print("2. 使用账户 testuser2 / testpass 登录")
        print("3. 点击左侧菜单的'调研管理'")
        print("4. 现在应该能看到调研列表")
    else:
        print("\n⚠️ 部分测试失败")

if __name__ == "__main__":
    main()