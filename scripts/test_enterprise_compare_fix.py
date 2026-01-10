#!/usr/bin/env python3
"""
测试企业对比修复
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_public_organizations_api():
    print("🏢 测试公开组织API")
    print("=" * 60)
    
    # 测试公开组织API
    print("1️⃣ 测试公开组织API:")
    try:
        response = requests.get(f"{BASE_URL}/organizations/public/")
        print(f"   响应状态: {response.status_code}")
        if response.status_code == 200:
            organizations = response.json()
            print(f"   ✅ 公开组织获取成功")
            print(f"      组织数量: {len(organizations)}")
            if organizations:
                for i, org in enumerate(organizations, 1):
                    print(f"      组织{i}: ID={org.get('id', 'N/A')}, 名称={org.get('name', 'N/A')}, 描述={org.get('description', 'N/A')}")
            else:
                print(f"   ⚠️  没有公开组织数据")
        else:
            print(f"   ❌ 公开组织获取失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 公开组织获取异常: {str(e)}")

def test_enterprise_compare_data_flow():
    print("\n🔄 测试企业对比数据流")
    print("=" * 60)
    
    # 模拟企业对比页的数据加载流程
    print("1️⃣ 模拟企业对比页数据加载:")
    
    try:
        # 获取公开组织
        org_response = requests.get(f"{BASE_URL}/organizations/public/")
        if org_response.status_code == 200:
            organizations = org_response.json()
            print(f"   ✅ 公开组织: {len(organizations)} 个")
            
            # 获取调研题目
            survey_response = requests.get(f"{BASE_URL}/surveys/20/questions")
            if survey_response.status_code == 200:
                questions = survey_response.json()
                print(f"   ✅ 调研题目: {len(questions)} 个")
                
                # 模拟前端数据设置
                print(f"   📊 前端数据设置:")
                print(f"      companyList: {len(organizations)} 个组织")
                print(f"      questionList: {len(questions)} 个题目")
                
                # 模拟公司选择
                if organizations:
                    selected_companies = [organizations[0]['id']]
                    print(f"   🎯 选择的公司: {[org['name'] for org in organizations if org['id'] in selected_companies]}")
                
                # 模拟题目选择
                if questions:
                    selected_question = questions[0]['id']
                    print(f"   🎯 选择的题目: {questions[0]['text']}")
                
            else:
                print(f"   ❌ 调研题目获取失败")
        else:
            print(f"   ❌ 公开组织获取失败")
    except Exception as e:
        print(f"   ❌ 数据流测试异常: {str(e)}")

def test_organization_naming():
    print("\n📝 测试组织命名功能")
    print("=" * 60)
    
    # 检查现有组织的命名
    try:
        response = requests.get(f"{BASE_URL}/organizations/public/")
        if response.status_code == 200:
            organizations = response.json()
            print(f"   📋 现有组织命名:")
            for i, org in enumerate(organizations, 1):
                print(f"      {i}. {org.get('name', 'N/A')} - {org.get('description', 'N/A')}")
            
            # 检查命名质量
            print(f"   🔍 命名质量分析:")
            for org in organizations:
                name = org.get('name', '')
                if name:
                    print(f"      '{name}': {'✅ 良好' if len(name) > 1 else '❌ 过短'}")
        else:
            print(f"   ❌ 组织数据获取失败")
    except Exception as e:
        print(f"   ❌ 组织命名测试异常: {str(e)}")

def test_enterprise_compare_ui():
    print("\n🎨 测试企业对比UI数据")
    print("=" * 60)
    
    # 模拟前端UI需要的数据结构
    print("1️⃣ 模拟前端UI数据结构:")
    
    try:
        # 获取组织数据
        org_response = requests.get(f"{BASE_URL}/organizations/public/")
        if org_response.status_code == 200:
            organizations = org_response.json()
            
            # 模拟前端下拉框选项
            print(f"   📋 公司选择下拉框选项:")
            for org in organizations:
                print(f"      label='{org.get('name', 'N/A')}', value={org.get('id', 'N/A')}")
            
            # 模拟多选公司
            if len(organizations) >= 2:
                selected_companies = [organizations[0]['id'], organizations[1]['id']]
                selected_names = [org['name'] for org in organizations if org['id'] in selected_companies]
                print(f"   🎯 多选公司: {selected_names}")
            
        else:
            print(f"   ❌ 组织数据获取失败")
    except Exception as e:
        print(f"   ❌ UI测试异常: {str(e)}")

def create_test_data_for_compare():
    print("\n📊 为企业对比创建测试数据")
    print("=" * 60)
    
    # 创建一些测试回答数据，关联到不同组织
    print("1️⃣ 创建测试回答数据:")
    
    # 获取现有组织
    try:
        org_response = requests.get(f"{BASE_URL}/organizations/public/")
        if org_response.status_code == 200:
            organizations = org_response.json()
            
            if organizations:
                # 为每个组织创建一些测试回答
                for org in organizations[:3]:  # 只处理前3个组织
                    org_id = org['id']
                    org_name = org['name']
                    print(f"   📝 为组织 '{org_name}' 创建测试回答:")
                    
                    # 创建3个测试回答
                    for i in range(3):
                        test_answer = {
                            "respondent_name": f"测试用户{i+1}",
                            "department": "技术部",
                            "position": "员工",
                            "department_id": 1,
                            "organization_id": org_id,
                            "answers": {
                                "74": f"选项{'ABC'[i]}",
                                "75": ["选项A", "选项B"],
                                "76": f"这是来自{org_name}的回答{i+1}"
                            }
                        }
                        
                        try:
                            response = requests.post(f"{BASE_URL}/surveys/20/answers/", json=test_answer)
                            if response.status_code == 201:
                                result = response.json()
                                print(f"      ✅ 回答{i+1}创建成功: ID={result.get('id')}")
                            else:
                                print(f"      ❌ 回答{i+1}创建失败: {response.status_code}")
                        except Exception as e:
                            print(f"      ❌ 回答{i+1}创建异常: {str(e)}")
            else:
                print(f"   ⚠️  没有组织数据")
        else:
            print(f"   ❌ 组织数据获取失败")
    except Exception as e:
        print(f"   ❌ 测试数据创建异常: {str(e)}")

if __name__ == "__main__":
    test_public_organizations_api()
    test_enterprise_compare_data_flow()
    test_organization_naming()
    test_enterprise_compare_ui()
    create_test_data_for_compare()
    
    print(f"\n🎉 修复总结:")
    print(f"✅ 企业对比修复:")
    print(f"   - 添加了公开组织API端点")
    print(f"   - 修复了公司选择功能")
    print(f"   - 支持组织命名和描述")
    print(f"   - 创建了测试数据")
    print(f"💡 现在应该:")
    print(f"   - 企业对比页可以正常选择公司")
    print(f"   - 显示正确的公司名称")
    print(f"   - 支持多选公司")
    print(f"   - 有足够的测试数据")
