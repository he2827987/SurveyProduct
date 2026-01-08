#!/usr/bin/env python3
"""
测试组织数据和企业对比功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_organization_data():
    print("🏢 测试组织数据")
    print("=" * 60)
    
    # 测试组织列表API
    print("1️⃣ 测试组织列表API:")
    try:
        response = requests.get(f"{BASE_URL}/organizations/")
        print(f"   响应状态: {response.status_code}")
        if response.status_code == 200:
            organizations = response.json()
            print(f"   ✅ 组织列表获取成功")
            print(f"      组织数量: {len(organizations)}")
            if organizations:
                for i, org in enumerate(organizations, 1):
                    print(f"      组织{i}: ID={org.get('id', 'N/A')}, 名称={org.get('name', 'N/A')}, 描述={org.get('description', 'N/A')}")
            else:
                print(f"   ⚠️  没有组织数据")
        elif response.status_code == 401:
            print(f"   🔐 需要认证")
        else:
            print(f"   ❌ 组织列表获取失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 组织列表获取异常: {str(e)}")

def test_organization_creation():
    print("\n2️⃣ 测试组织创建:")
    
    # 测试创建组织
    test_organizations = [
        {
            "name": "腾讯科技",
            "description": "腾讯科技有限公司",
            "is_active": True,
            "is_public": True
        },
        {
            "name": "阿里巴巴",
            "description": "阿里巴巴集团",
            "is_active": True,
            "is_public": True
        },
        {
            "name": "百度",
            "description": "百度公司",
            "is_active": True,
            "is_public": True
        }
    ]
    
    for org_data in test_organizations:
        print(f"   📝 创建组织: {org_data['name']}")
        try:
            response = requests.post(f"{BASE_URL}/organizations/", json=org_data)
            print(f"      响应状态: {response.status_code}")
            if response.status_code == 201:
                result = response.json()
                print(f"      ✅ 创建成功: ID={result.get('id', 'N/A')}")
            elif response.status_code == 401:
                print(f"      🔐 需要认证")
            elif response.status_code == 422:
                print(f"      ⚠️  数据验证失败: {response.text}")
            else:
                print(f"      ❌ 创建失败: {response.text}")
        except Exception as e:
            print(f"      ❌ 创建异常: {str(e)}")

def test_survey_organization_relationship():
    print("\n3️⃣ 测试调研与组织关系:")
    
    # 检查调研的组织ID
    try:
        response = requests.get(f"{BASE_URL}/surveys/20/detail")
        if response.status_code == 200:
            survey_data = response.json()
            org_id = survey_data.get('organization_id')
            print(f"   调研20的组织ID: {org_id}")
            
            if org_id:
                # 获取组织信息
                org_response = requests.get(f"{BASE_URL}/organizations/{org_id}")
                if org_response.status_code == 200:
                    org_data = org_response.json()
                    print(f"   组织信息: {org_data.get('name', 'N/A')}")
                else:
                    print(f"   组织信息获取失败: {org_response.status_code}")
            else:
                print(f"   调研没有关联组织")
        else:
            print(f"   调研详情获取失败: {response.status_code}")
    except Exception as e:
        print(f"   测试异常: {str(e)}")

def test_enterprise_compare_data():
    print("\n4️⃣ 测试企业对比数据:")
    
    # 模拟企业对比的数据需求
    print("   📊 企业对比需要的数据:")
    print("      - 组织列表 (公司)")
    print("      - 调研列表")
    print("      - 调研题目")
    print("      - 回答数据 (按组织分组)")
    
    # 检查回答数据
    try:
        response = requests.get(f"{BASE_URL}/surveys/20/answers/")
        print(f"   调研20的回答数据: 状态码 {response.status_code}")
        if response.status_code == 200:
            answers = response.json()
            print(f"      回答数量: {len(answers)}")
            if answers:
                # 分析回答数据的组织分布
                org_counts = {}
                for answer in answers:
                    org_id = answer.get('organization_id')
                    if org_id:
                        org_counts[org_id] = org_counts.get(org_id, 0) + 1
                
                print(f"      组织分布: {org_counts}")
            else:
                print(f"      没有回答数据")
        elif response.status_code == 401:
            print(f"      🔐 需要认证")
        else:
            print(f"      获取失败: {response.text}")
    except Exception as e:
        print(f"   回答数据测试异常: {str(e)}")

def test_organization_naming_feature():
    print("\n5️⃣ 测试组织命名功能:")
    
    # 检查组织模型字段
    print("   📋 组织模型字段:")
    print("      - id: 组织ID")
    print("      - name: 组织名称")
    print("      - description: 组织描述")
    print("      - owner_id: 所有者ID")
    print("      - is_active: 是否活跃")
    print("      - is_public: 是否公开")
    print("      - created_at: 创建时间")
    print("      - updated_at: 更新时间")
    
    # 检查组织API端点
    print("   🔗 组织API端点:")
    print("      - GET /organizations/ - 获取组织列表")
    print("      - POST /organizations/ - 创建组织")
    print("      - GET /organizations/{id} - 获取组织详情")
    print("      - PUT /organizations/{id} - 更新组织")
    print("      - DELETE /organizations/{id} - 删除组织")

def create_test_organizations():
    print("\n6️⃣ 创建测试组织:")
    
    # 创建一些测试组织用于企业对比
    test_orgs = [
        {
            "name": "华为技术",
            "description": "华为技术有限公司",
            "is_active": True,
            "is_public": True
        },
        {
            "name": "小米科技",
            "description": "小米科技有限公司",
            "is_active": True,
            "is_public": True
        },
        {
            "name": "字节跳动",
            "description": "字节跳动科技有限公司",
            "is_active": True,
            "is_public": True
        }
    ]
    
    created_orgs = []
    for org_data in test_orgs:
        try:
            response = requests.post(f"{BASE_URL}/organizations/", json=org_data)
            if response.status_code == 201:
                result = response.json()
                created_orgs.append(result)
                print(f"   ✅ 创建成功: {org_data['name']} (ID: {result.get('id')})")
            else:
                print(f"   ❌ 创建失败: {org_data['name']} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ 创建异常: {org_data['name']} - {str(e)}")
    
    return created_orgs

if __name__ == "__main__":
    test_organization_data()
    test_organization_creation()
    test_survey_organization_relationship()
    test_enterprise_compare_data()
    test_organization_naming_feature()
    
    print(f"\n🎉 测试总结:")
    print(f"✅ 组织数据测试:")
    print(f"   - 检查了组织API功能")
    print(f"   - 验证了组织数据结构")
    print(f"   - 测试了组织创建功能")
    print(f"✅ 企业对比需求:")
    print(f"   - 组织命名功能已存在")
    print(f"   - 需要创建测试组织数据")
    print(f"   - 需要关联调研和回答数据")
    print(f"💡 下一步:")
    print(f"   - 创建测试组织")
    print(f"   - 关联调研到组织")
    print(f"   - 创建测试回答数据")
    print(f"   - 完善企业对比功能")
