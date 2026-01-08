#!/usr/bin/env python3
"""
通用测试脚本 - 整合常用测试功能
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"

def test_basic_connectivity():
    """测试基本连接性"""
    print("🔗 测试基本连接性")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端服务连接失败: {str(e)}")
        return False
    return True

def test_organization_api():
    """测试组织API"""
    print("\n🏢 测试组织API")
    print("=" * 50)
    
    # 测试公开组织API
    try:
        response = requests.get(f"{BASE_URL}/organizations/public/")
        if response.status_code == 200:
            organizations = response.json()
            print(f"✅ 公开组织API正常，共 {len(organizations)} 个组织")
            if organizations:
                print("   前3个组织:")
                for i, org in enumerate(organizations[:3], 1):
                    print(f"   {i}. {org.get('name', 'N/A')} (ID: {org.get('id', 'N/A')})")
        else:
            print(f"❌ 公开组织API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 组织API测试异常: {str(e)}")

def test_survey_api():
    """测试调研API"""
    print("\n📊 测试调研API")
    print("=" * 50)
    
    # 测试调研详情API
    try:
        response = requests.get(f"{BASE_URL}/surveys/20/detail")
        if response.status_code == 200:
            survey = response.json()
            print(f"✅ 调研详情API正常")
            print(f"   调研: {survey.get('title', 'N/A')}")
            print(f"   题目数量: {len(survey.get('questions', []))}")
        else:
            print(f"❌ 调研详情API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 调研API测试异常: {str(e)}")

def test_analytics_api():
    """测试数据分析API"""
    print("\n📈 测试数据分析API")
    print("=" * 50)
    
    # 测试分析数据API
    try:
        response = requests.get(f"{BASE_URL}/organizations/2/analytics/overview")
        if response.status_code == 200:
            data = response.json()
            print("✅ 数据分析API正常")
            print(f"   数据项: {len(data)} 个")
        else:
            print(f"❌ 数据分析API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 数据分析API测试异常: {str(e)}")

def test_enterprise_compare_data():
    """测试企业对比数据"""
    print("\n🏭 测试企业对比数据")
    print("=" * 50)
    
    try:
        # 获取组织数据
        org_response = requests.get(f"{BASE_URL}/organizations/public/")
        if org_response.status_code == 200:
            organizations = org_response.json()
            print(f"✅ 组织数据: {len(organizations)} 个")
            
            # 获取调研题目
            survey_response = requests.get(f"{BASE_URL}/surveys/20/questions")
            if survey_response.status_code == 200:
                questions = survey_response.json()
                print(f"✅ 调研题目: {len(questions)} 个")
                
                # 检查回答数据
                answers_response = requests.get(f"{BASE_URL}/surveys/20/answers/")
                if answers_response.status_code == 200:
                    answers = answers_response.json()
                    print(f"✅ 回答数据: {len(answers)} 个")
                    
                    # 分析组织分布
                    org_counts = {}
                    for answer in answers:
                        org_id = answer.get('organization_id')
                        if org_id:
                            org_counts[org_id] = org_counts.get(org_id, 0) + 1
                    
                    print(f"   组织分布: {org_counts}")
                else:
                    print(f"❌ 回答数据获取失败: {answers_response.status_code}")
            else:
                print(f"❌ 调研题目获取失败: {survey_response.status_code}")
        else:
            print(f"❌ 组织数据获取失败: {org_response.status_code}")
    except Exception as e:
        print(f"❌ 企业对比数据测试异常: {str(e)}")

def test_mobile_survey():
    """测试移动端调研功能"""
    print("\n📱 测试移动端调研功能")
    print("=" * 50)
    
    try:
        # 测试调研填写页面
        response = requests.get(f"{BASE_URL}/surveys/20/fill")
        if response.status_code == 200:
            data = response.json()
            print("✅ 移动端调研页面正常")
            print(f"   调研标题: {data.get('title', 'N/A')}")
            print(f"   组织ID: {data.get('organization_id', 'N/A')}")
        else:
            print(f"❌ 移动端调研页面失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 移动端调研测试异常: {str(e)}")

def create_test_data():
    """创建测试数据"""
    print("\n📝 创建测试数据")
    print("=" * 50)
    
    # 为不同组织创建测试回答
    try:
        org_response = requests.get(f"{BASE_URL}/organizations/public/")
        if org_response.status_code == 200:
            organizations = org_response.json()
            
            if organizations:
                # 为前3个组织创建测试回答
                for org in organizations[:3]:
                    org_id = org['id']
                    org_name = org['name']
                    print(f"   为组织 '{org_name}' 创建测试回答...")
                    
                    test_answer = {
                        "respondent_name": f"测试用户_{org_name}",
                        "department": "技术部",
                        "position": "员工",
                        "department_id": 1,
                        "organization_id": org_id,
                        "answers": {
                            "74": "选项A",
                            "75": ["选项A", "选项B"],
                            "76": f"这是来自{org_name}的测试回答"
                        }
                    }
                    
                    response = requests.post(f"{BASE_URL}/surveys/20/answers/", json=test_answer)
                    if response.status_code == 201:
                        print(f"   ✅ 创建成功")
                    else:
                        print(f"   ❌ 创建失败: {response.status_code}")
            else:
                print("   ⚠️  没有组织数据")
        else:
            print("   ❌ 组织数据获取失败")
    except Exception as e:
        print(f"   ❌ 测试数据创建异常: {str(e)}")

def main():
    """主函数"""
    print("🚀 开始全面测试")
    print("=" * 60)
    
    # 测试基本连接性
    if not test_basic_connectivity():
        print("\n❌ 基本连接测试失败，请检查后端服务")
        return
    
    # 运行各项测试
    test_organization_api()
    test_survey_api()
    test_analytics_api()
    test_enterprise_compare_data()
    test_mobile_survey()
    
    # 询问是否创建测试数据
    print("\n" + "=" * 60)
    print("💡 测试完成！")
    print("\n可选操作:")
    print("1. 创建测试数据 (输入 'create')")
    print("2. 退出 (输入其他任意内容)")
    
    choice = input("\n请选择: ").strip().lower()
    if choice == 'create':
        create_test_data()
    
    print("\n🎉 测试结束")

if __name__ == "__main__":
    main()
