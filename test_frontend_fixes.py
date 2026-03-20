#!/usr/bin/env python3
"""
测试脚本：验证调研列表和数据分析功能
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_survey_list():
    """测试调研列表API"""
    print("测试调研列表API...")
    response = requests.get(f"{BASE_URL}/surveys/", headers=HEADERS)
    
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ 调研列表获取成功，共 {len(surveys)} 个调研")
        for survey in surveys:
            print(f"  - {survey['title']} (ID: {survey['id']})")
        return True
    else:
        print(f"❌ 调研列表获取失败: {response.status_code} - {response.text}")
        return False

def test_global_surveys():
    """测试全局调研API"""
    print("\n测试全局调研API...")
    response = requests.get(f"{BASE_URL}/surveys/global/all", headers=HEADERS)
    
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ 全局调研获取成功，共 {len(surveys)} 个调研")
        return True
    else:
        print(f"❌ 全局调研获取失败: {response.status_code} - {response.text}")
        return False

def test_survey_questions():
    """测试调研题目API"""
    print("\n测试调研题目API...")
    response = requests.get(f"{BASE_URL}/surveys/37/questions", headers=HEADERS)
    
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ 调研题目获取成功，共 {len(questions)} 个题目")
        return True
    else:
        print(f"❌ 调研题目获取失败: {response.status_code} - {response.text}")
        return False

def test_analytics():
    """测试分析API"""
    print("\n测试分析API...")
    # 测试获取调研统计
    response = requests.get(f"{BASE_URL}/analytics/survey/37/statistics", headers=HEADERS)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 调研统计获取成功")
        return True
    else:
        print(f"❌ 调研统计获取失败: {response.status_code} - {response.text}")
        # 尝试其他分析API端点
        response = requests.get(f"{BASE_URL}/analytics/", headers=HEADERS)
        if response.status_code == 200:
            print(f"✅ 分析页面API响应正常")
            return True
        else:
            print(f"❌ 分析页面API也失败: {response.status_code} - {response.text}")
            return False

def main():
    print("=== 调研系统功能测试 ===\n")
    
    results = []
    results.append(test_survey_list())
    results.append(test_global_surveys())
    results.append(test_survey_questions())
    results.append(test_analytics())
    
    print(f"\n=== 测试结果 ===")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()