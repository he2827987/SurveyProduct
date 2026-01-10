#!/usr/bin/env python3
import requests
import json
import time

def test_advanced_analytics():
    """测试高级数据分析功能"""
    base_url = "http://localhost:8000"
    
    print("=== 测试高级数据分析功能 ===\n")
    
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
    print("登录成功")
    
    # 2. 测试交叉分析
    print("\n2. 测试交叉分析...")
    # 分析问题35（工作环境满意度）和问题36（薪资待遇）的关系
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/analytics/cross-analysis?survey_id=1&question1_id=35&question2_id=36", 
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ 交叉分析获取成功")
        print(f"   问题1: {data['question1']['text']}")
        print(f"   问题2: {data['question2']['text']}")
        print(f"   交叉分析结果:")
        for response1, responses2 in data['cross_analysis'].items():
            print(f"     {response1}:")
            for response2, count in responses2.items():
                print(f"       -> {response2}: {count} 人")
    else:
        print(f"❌ 交叉分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 3. 测试数据导出
    print("\n3. 测试数据导出...")
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/analytics/export?survey_id=1", 
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ 数据导出获取成功")
        print(f"   调研标题: {data['survey_title']}")
        print(f"   总记录数: {data['total_records']}")
        print(f"   数据示例:")
        if data['data']:
            sample = data['data'][0]
            for key, value in sample.items():
                if key != 'answer_id' and value is not None:
                    print(f"     {key}: {value}")
    else:
        print(f"❌ 数据导出获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 4. 测试组织概览导出
    print("\n4. 测试组织概览导出...")
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/analytics/export", 
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ 组织概览导出获取成功")
        print(f"   总调研数: {data['total_surveys']}")
        print(f"   总参与者数: {data['total_participants']}")
        print(f"   调研列表:")
        for survey in data['surveys']:
            print(f"     - {survey['title']} (ID: {survey['id']})")
        print(f"   参与者列表:")
        for participant in data['participants'][:3]:  # 只显示前3个
            print(f"     - {participant['name']} ({participant['position']})")
    else:
        print(f"❌ 组织概览导出获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 5. 测试趋势分析（30天）
    print("\n5. 测试长期趋势分析...")
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/analytics/trends?days=30", 
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ 长期趋势分析获取成功")
        print(f"   分析天数: {data['period_days']}")
        print(f"   总答案数: {data['total_answers']}")
        print(f"   趋势数据: {len(data['trend_data'])} 条记录")
        
        # 显示有数据的日期
        active_days = [t for t in data['trend_data'] if t['answers'] > 0]
        if active_days:
            print(f"   活跃日期:")
            for trend in active_days:
                print(f"     {trend['date']}: {trend['answers']} 答案, {trend['unique_participants']} 参与者")
        else:
            print("   暂无活跃数据")
    else:
        print(f"❌ 长期趋势分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 6. 测试详细调研分析（显示更多信息）
    print("\n6. 测试详细调研分析...")
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/surveys/1/analytics", 
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ 详细调研分析获取成功")
        print(f"   调研标题: {data['survey_title']}")
        print(f"   总答案数: {data['total_answers']}")
        print(f"   问题分析: {len(data['question_analytics'])} 个问题")
        
        # 显示每个问题的分析
        for i, question in enumerate(data['question_analytics'], 1):
            print(f"\n   问题{i}: {question['question_text']}")
            print(f"     类型: {question['question_type']}")
            print(f"     回答数: {question['total_responses']}")
            print(f"     回答分布:")
            for response, count in question['response_distribution'].items():
                percentage = (count / question['total_responses'] * 100) if question['total_responses'] > 0 else 0
                print(f"       {response}: {count} 人 ({percentage:.1f}%)")
    else:
        print(f"❌ 详细调研分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print("\n=== 高级数据分析功能测试完成 ===")

if __name__ == "__main__":
    test_advanced_analytics()
