#!/usr/bin/env python3
import requests
import json
import time

def test_analytics_api():
    """测试数据分析API"""
    base_url = "http://localhost:8000"
    
    print("=== 测试数据分析API ===\n")
    
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
    
    # 2. 测试调研概览
    print("\n2. 测试调研概览...")
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/overview", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 调研概览获取成功")
        print(f"   总调研数: {data['total_surveys']}")
        print(f"   总答案数: {data['total_answers']}")
        print(f"   总参与者数: {data['total_participants']}")
        print(f"   平均答案数: {data['average_answers_per_survey']:.2f}")
        print(f"   每日趋势: {data['daily_trend']}")
    else:
        print(f"❌ 调研概览获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 3. 测试参与者分析
    print("\n3. 测试参与者分析...")
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/participants", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 参与者分析获取成功")
        print(f"   总参与者数: {data['total_participants']}")
        print(f"   活跃参与者数: {data['active_participants']}")
        print(f"   参与率: {data['participation_rate']:.2f}%")
        print(f"   按部门统计: {data['by_department']}")
        print(f"   按职位统计: {data['by_position']}")
    else:
        print(f"❌ 参与者分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 4. 测试趋势分析
    print("\n4. 测试趋势分析...")
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/trends?days=7", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 趋势分析获取成功")
        print(f"   分析天数: {data['period_days']}")
        print(f"   总答案数: {data['total_answers']}")
        print(f"   趋势数据: {len(data['trend_data'])} 条记录")
        for trend in data['trend_data'][:3]:  # 只显示前3条
            print(f"     {trend['date']}: {trend['answers']} 答案, {trend['unique_participants']} 参与者")
    else:
        print(f"❌ 趋势分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 5. 测试特定调研分析（使用已知的调研ID）
    print("\n5. 测试特定调研分析...")
    survey_id = 1  # 使用我们创建的调研ID
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/{survey_id}/analytics", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 调研详细分析获取成功")
        print(f"   调研标题: {data['survey_title']}")
        print(f"   总答案数: {data['total_answers']}")
        print(f"   问题分析: {len(data['question_analytics'])} 个问题")
        print(f"   参与者分析: {data['participant_analysis']['total_participants']} 个参与者")
        
        # 显示第一个问题的分析
        if data['question_analytics']:
            first_q = data['question_analytics'][0]
            print(f"   第一个问题: {first_q['question_text']}")
            print(f"     回答数: {first_q['total_responses']}")
            print(f"     回答分布: {first_q['response_distribution']}")
            
            # 显示第二个问题的分析（多选题）
            if len(data['question_analytics']) > 2:
                second_q = data['question_analytics'][2]
                print(f"   第三个问题（多选题）: {second_q['question_text']}")
                print(f"     回答数: {second_q['total_responses']}")
                print(f"     回答分布: {second_q['response_distribution']}")
    else:
        print(f"❌ 调研详细分析获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print("\n=== 数据分析API测试完成 ===")

if __name__ == "__main__":
    test_analytics_api()
