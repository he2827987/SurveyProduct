#!/usr/bin/env python3
"""
综合测试套件
测试survey product的所有主要功能
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "test_details": []
}

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.start_time = time.time()
        self.end_time = None
        self.duration = 0

    def set_passed(self, message: str = ""):
        self.passed = True
        self.message = message
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def set_failed(self, message: str):
        self.passed = False
        self.message = message
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def to_dict(self):
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "duration": round(self.duration, 3)
        }

def run_test(test_name: str, test_func):
    """运行单个测试"""
    global TEST_RESULTS
    
    TEST_RESULTS["total_tests"] += 1
    result = TestResult(test_name)
    
    try:
        test_func()
        result.set_passed("测试通过")
        TEST_RESULTS["passed_tests"] += 1
        print(f"✅ {test_name} - 通过 ({result.duration:.3f}s)")
    except Exception as e:
        result.set_failed(str(e))
        TEST_RESULTS["failed_tests"] += 1
        print(f"❌ {test_name} - 失败: {str(e)} ({result.duration:.3f}s)")
    
    TEST_RESULTS["test_details"].append(result.to_dict())

def get_auth_headers(username: str = "admin", password: str = "admin123") -> Dict[str, str]:
    """获取认证头"""
    response = requests.post(f"{BASE_URL}/users/login/access-token", data={
        "username": username,
        "password": password
    })
    
    if response.status_code != 200:
        raise Exception(f"登录失败: {response.status_code} - {response.text}")
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ===== 测试用例 =====

def test_api_connectivity():
    """测试API连通性"""
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code != 200:
        raise Exception(f"健康检查失败: {response.status_code}")

def test_user_authentication():
    """测试用户认证"""
    headers = get_auth_headers()
    
    # 测试获取用户信息
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取用户信息失败: {response.status_code}")

def test_survey_management():
    """测试调研管理功能"""
    headers = get_auth_headers()
    
    # 创建测试调研
    survey_data = {
        "title": "测试调研_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "description": "这是一个自动化测试创建的调研",
        "created_by_user_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/surveys/", json=survey_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建调研失败: {response.status_code} - {response.text}")
    
    survey_id = response.json()["id"]
    
    # 获取调研列表
    response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取调研列表失败: {response.status_code}")
    
    # 删除测试调研
    response = requests.delete(f"{BASE_URL}/surveys/{survey_id}", headers=headers)
    if response.status_code not in [200, 204]:
        raise Exception(f"删除调研失败: {response.status_code}")

def test_question_management():
    """测试问题管理功能"""
    headers = get_auth_headers()
    
    # 创建测试问题
    question_data = {
        "text": "测试问题_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "type": "SINGLE_CHOICE",
        "options": json.dumps([
            {"text": "选项1", "score": 1},
            {"text": "选项2", "score": 2}
        ]),
        "is_required": True,
        "min_score": 1,
        "max_score": 2
    }
    
    response = requests.post(f"{BASE_URL}/questions/", json=question_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建问题失败: {response.status_code} - {response.text}")
    
    question_id = response.json()["id"]
    
    # 获取问题列表
    response = requests.get(f"{BASE_URL}/questions/", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取问题列表失败: {response.status_code}")
    
    # 更新问题
    update_data = {
        "text": "更新的测试问题_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    }
    response = requests.put(f"{BASE_URL}/questions/{question_id}", json=update_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"更新问题失败: {response.status_code}")

def test_tag_management():
    """测试标签管理功能"""
    headers = get_auth_headers()
    
    # 创建测试标签
    tag_data = {
        "name": "测试标签_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "color": "#FF0000",
        "description": "这是一个自动化测试创建的标签"
    }
    
    response = requests.post(f"{BASE_URL}/tags/", json=tag_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建标签失败: {response.status_code} - {response.text}")
    
    tag_id = response.json()["id"]
    
    # 获取标签列表
    response = requests.get(f"{BASE_URL}/tags/", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取标签列表失败: {response.status_code}")
    
    # 测试问题标签关联
    question_data = {
        "text": "带标签的测试问题",
        "type": "SINGLE_CHOICE",
        "options": json.dumps([{"text": "选项1", "score": 1}]),
        "is_required": True
    }
    
    response = requests.post(f"{BASE_URL}/questions/", json=question_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建问题失败: {response.status_code}")
    
    question_id = response.json()["id"]
    
    # 关联标签
    response = requests.post(f"{BASE_URL}/questions/{question_id}/tags/{tag_id}", headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"关联标签失败: {response.status_code}")

def test_analytics_functionality():
    """测试分析功能"""
    headers = get_auth_headers()
    
    # 创建测试调研和问题
    survey_data = {
        "title": "分析测试调研",
        "description": "用于测试分析功能的调研",
        "created_by_user_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/surveys/", json=survey_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建调研失败: {response.status_code}")
    
    survey_id = response.json()["id"]
    
    # 添加问题到调研
    question_data = {
        "text": "分析测试问题",
        "type": "SINGLE_CHOICE",
        "options": json.dumps([
            {"text": "选项1", "score": 1},
            {"text": "选项2", "score": 2}
        ]),
        "is_required": True
    }
    
    response = requests.post(f"{BASE_URL}/questions/", json=question_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建问题失败: {response.status_code}")
    
    question_id = response.json()["id"]
    
    response = requests.post(f"{BASE_URL}/surveys/{survey_id}/questions/", 
                           json={"question_id": question_id, "order": 1}, 
                           headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"添加问题到调研失败: {response.status_code}")
    
    # 测试分析API
    response = requests.get(f"{BASE_URL}/organizations/1/analytics/overview", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取组织概览失败: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/organizations/1/surveys/{survey_id}/analytics", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取调研分析失败: {response.status_code}")

def test_tag_analytics():
    """测试标签分析功能"""
    headers = get_auth_headers()
    
    # 测试组织标签分析
    response = requests.get(f"{BASE_URL}/organizations/1/analytics/tags", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取组织标签分析失败: {response.status_code}")
    
    # 测试标签汇总统计
    response = requests.get(f"{BASE_URL}/organizations/1/analytics/tags/summary", headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取标签汇总统计失败: {response.status_code}")

def test_enterprise_comparison():
    """测试企业对比功能"""
    headers = get_auth_headers()
    
    # 创建测试调研
    survey_data = {
        "title": "企业对比测试调研",
        "description": "用于测试企业对比功能的调研",
        "created_by_user_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/surveys/", json=survey_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"创建调研失败: {response.status_code}")
    
    survey_id = response.json()["id"]
    
    # 准备对比数据
    comparison_data = {
        "dimension": "员工满意度",
        "companies": ["公司A", "公司B"],
        "comparison_data": [
            {"company": "公司A", "score": 85, "satisfaction": 90},
            {"company": "公司B", "score": 78, "satisfaction": 82}
        ]
    }
    
    # 测试企业对比AI分析
    response = requests.post(f"{BASE_URL}/organizations/1/surveys/{survey_id}/analytics/enterprise-comparison-ai", 
                           json=comparison_data, headers=headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"企业对比AI分析失败: {response.status_code}")

def test_database_connectivity():
    """测试数据库连接"""
    headers = get_auth_headers()
    
    # 测试获取用户列表（需要数据库连接）
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    if response.status_code != 200:
        raise Exception(f"数据库连接测试失败: {response.status_code}")

def test_question_types():
    """测试所有问题类型"""
    headers = get_auth_headers()
    
    question_types = [
        "SINGLE_CHOICE",
        "MULTI_CHOICE", 
        "TEXT_INPUT",
        "NUMBER_INPUT"
    ]
    
    for qtype in question_types:
        question_data = {
            "text": f"测试{qtype}问题",
            "type": qtype,
            "options": json.dumps([
                {"text": "选项1", "score": 1},
                {"text": "选项2", "score": 2}
            ]) if qtype in ["SINGLE_CHOICE", "MULTI_CHOICE"] else None,
            "is_required": True,
            "min_score": 1,
            "max_score": 2
        }
        
        response = requests.post(f"{BASE_URL}/questions/", json=question_data, headers=headers)
        if response.status_code not in [200, 201]:
            raise Exception(f"创建{qtype}问题失败: {response.status_code}")

def test_environment_configuration():
    """测试环境配置"""
    # 检查必需的环境变量
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'ENVIRONMENT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise Exception(f"缺失环境变量: {', '.join(missing_vars)}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行综合测试套件")
    print("=" * 60)
    
    test_cases = [
        ("API连通性测试", test_api_connectivity),
        ("环境配置测试", test_environment_configuration),
        ("用户认证测试", test_user_authentication),
        ("数据库连接测试", test_database_connectivity),
        ("调研管理测试", test_survey_management),
        ("问题管理测试", test_question_management),
        ("标签管理测试", test_tag_management),
        ("问题类型测试", test_question_types),
        ("分析功能测试", test_analytics_functionality),
        ("标签分析测试", test_tag_analytics),
        ("企业对比测试", test_enterprise_comparison)
    ]
    
    for test_name, test_func in test_cases:
        run_test(test_name, test_func)
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"总测试数: {TEST_RESULTS['total_tests']}")
    print(f"通过测试: {TEST_RESULTS['passed_tests']}")
    print(f"失败测试: {TEST_RESULTS['failed_tests']}")
    print(f"成功率: {(TEST_RESULTS['passed_tests'] / TEST_RESULTS['total_tests'] * 100):.1f}%")
    
    if TEST_RESULTS["failed_tests"] > 0:
        print("\n❌ 失败的测试:")
        for test in TEST_RESULTS["test_details"]:
            if not test["passed"]:
                print(f"   - {test['name']}: {test['message']}")
    
    # 生成测试报告文件
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细测试报告已保存到: {report_file}")
    
    return TEST_RESULTS["failed_tests"] == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)