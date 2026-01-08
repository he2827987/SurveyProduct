#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def demo_analytics():
    """演示数据分析的实际应用"""
    base_url = "http://localhost:8000"
    
    print("🎯 调研平台数据分析演示")
    print("=" * 50)
    
    # 登录
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/api/v1/users/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ 登录成功")
    print()
    
    # 1. 组织概览分析
    print("📊 1. 组织概览分析")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/overview", headers=headers)
    data = response.json()
    
    print(f"📈 总调研数: {data['total_surveys']}")
    print(f"📝 总答案数: {data['total_answers']}")
    print(f"👥 总参与者数: {data['total_participants']}")
    print(f"📊 平均答案数: {data['average_answers_per_survey']:.1f}")
    
    # 显示最近活跃情况
    active_days = [k for k, v in data['daily_trend'].items() if v > 0]
    if active_days:
        print(f"🔥 最近活跃日期: {', '.join(active_days[-3:])}")
    print()
    
    # 2. 参与者分析
    print("👥 2. 参与者分析")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/participants", headers=headers)
    data = response.json()
    
    print(f"📊 总参与者: {data['total_participants']} 人")
    print(f"✅ 活跃参与者: {data['active_participants']} 人")
    print(f"📈 参与率: {data['participation_rate']:.1f}%")
    
    # 显示部门分布
    if data['by_department']:
        print("🏢 部门分布:")
        for dept, info in data['by_department'].items():
            print(f"   {dept}: {info['count']} 人")
    print()
    
    # 3. 调研详细分析
    print("📋 3. 调研详细分析")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics", headers=headers)
    data = response.json()
    
    print(f"📝 调研标题: {data['survey_title']}")
    print(f"📊 总答案数: {data['total_answers']}")
    print(f"❓ 问题数量: {len(data['question_analytics'])}")
    
    # 显示关键问题分析
    for i, question in enumerate(data['question_analytics'][:3], 1):
        print(f"\n❓ 问题{i}: {question['question_text']}")
        print(f"   回答数: {question['total_responses']}")
        
        # 显示主要回答
        sorted_responses = sorted(question['response_distribution'].items(), 
                                key=lambda x: x[1], reverse=True)
        for response, count in sorted_responses[:3]:
            percentage = (count / question['total_responses'] * 100)
            print(f"   • {response}: {count} 人 ({percentage:.1f}%)")
    print()
    
    # 4. 交叉分析
    print("🔗 4. 交叉分析")
    print("-" * 30)
    response = requests.get(
        f"{base_url}/api/v1/organizations/6/analytics/cross-analysis?survey_id=1&question1_id=35&question2_id=36", 
        headers=headers
    )
    data = response.json()
    
    print(f"❓ 问题1: {data['question1']['text']}")
    print(f"❓ 问题2: {data['question2']['text']}")
    print("🔍 交叉分析结果:")
    
    for response1, responses2 in data['cross_analysis'].items():
        print(f"   📊 {response1}:")
        for response2, count in responses2.items():
            print(f"      → {response2}: {count} 人")
    print()
    
    # 5. 趋势分析
    print("📈 5. 趋势分析")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/analytics/trends?days=7", headers=headers)
    data = response.json()
    
    print(f"📅 分析周期: {data['period_days']} 天")
    print(f"📊 总答案数: {data['total_answers']}")
    
    # 显示活跃日期
    active_trends = [t for t in data['trend_data'] if t['answers'] > 0]
    if active_trends:
        print("📅 活跃日期:")
        for trend in active_trends:
            print(f"   {trend['date']}: {trend['answers']} 答案, {trend['unique_participants']} 参与者")
    print()
    
    # 6. 数据洞察总结
    print("💡 6. 数据洞察总结")
    print("-" * 30)
    
    # 重新获取数据用于总结
    overview = requests.get(f"{base_url}/api/v1/organizations/6/analytics/overview", headers=headers).json()
    participants = requests.get(f"{base_url}/api/v1/organizations/6/analytics/participants", headers=headers).json()
    survey_detail = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics", headers=headers).json()
    
    print("🎯 关键发现:")
    
    # 参与情况
    participation_rate = participants['participation_rate']
    if participation_rate > 50:
        print(f"✅ 参与率良好 ({participation_rate:.1f}%)")
    else:
        print(f"⚠️  参与率偏低 ({participation_rate:.1f}%)，建议加强推广")
    
    # 答案分布分析
    if survey_detail['question_analytics']:
        first_q = survey_detail['question_analytics'][0]
        responses = first_q['response_distribution']
        negative_responses = sum(count for response, count in responses.items() 
                               if '不满意' in response or '非常不满意' in response)
        total_responses = first_q['total_responses']
        negative_rate = (negative_responses / total_responses * 100) if total_responses > 0 else 0
        
        if negative_rate > 50:
            print(f"⚠️  满意度偏低 ({negative_rate:.1f}% 不满意)，需要关注")
        else:
            print(f"✅ 满意度良好 ({negative_rate:.1f}% 不满意)")
    
    # 趋势分析
    if overview['daily_trend']:
        recent_activity = sum(overview['daily_trend'].values())
        if recent_activity > 0:
            print(f"📈 最近7天有 {recent_activity} 个新答案，调研活跃")
        else:
            print("📉 最近7天无新答案，建议重新推广")
    
    print()
    print("🎉 数据分析演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    demo_analytics()
