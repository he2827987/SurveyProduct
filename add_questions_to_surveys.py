#!/usr/bin/env python3
"""
为调研添加问题
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("🔧 为调研添加问题")
    print("=" * 50)
    
    # 1. 登录
    print("🔐 正在登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取组织2的调研
    print("\n📋 获取组织2的调研:")
    try:
        response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
        if response.status_code == 200:
            surveys = response.json()
            org2_surveys = [s for s in surveys if s.get('organization_id') == 2]
            print(f"✅ 组织2有 {len(org2_surveys)} 个调研")
            for survey in org2_surveys:
                print(f"   ID: {survey['id']}, 标题: {survey['title']}")
        else:
            print(f"❌ 获取调研列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取调研列表异常: {str(e)}")
        return
    
    # 3. 为调研15添加问题
    print("\n➕ 为调研15添加问题:")
    survey_id = 15
    
    # 问题列表
    questions = [
        {
            "text": "您对当前的工作环境满意度如何？",
            "type": "single_choice",
            "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"],
            "is_required": True
        },
        {
            "text": "您认为公司的薪资待遇如何？",
            "type": "single_choice",
            "options": ["很有竞争力", "有竞争力", "一般", "偏低", "很低"],
            "is_required": True
        },
        {
            "text": "您认为公司需要改进的方面有哪些？（可多选）",
            "type": "multi_choice",
            "options": ["工作环境", "薪资福利", "培训机会", "晋升机制", "团队协作", "工作压力", "其他"],
            "is_required": False
        },
        {
            "text": "您对公司有什么建议或意见？",
            "type": "text_input",
            "is_required": False
        }
    ]
    
    for i, question_data in enumerate(questions):
        try:
            print(f"   添加问题 {i+1}: {question_data['text'][:30]}...")
            response = requests.post(f"{BASE_URL}/surveys/{survey_id}/questions/", json=question_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ 问题 {i+1} 添加成功")
            else:
                print(f"   ❌ 问题 {i+1} 添加失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ 问题 {i+1} 添加异常: {str(e)}")
    
    # 4. 为调研14添加问题
    print("\n➕ 为调研14添加问题:")
    survey_id = 14
    
    questions_14 = [
        {
            "text": "您对团队协作的满意度如何？",
            "type": "single_choice",
            "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"],
            "is_required": True
        },
        {
            "text": "您认为团队沟通是否顺畅？",
            "type": "single_choice",
            "options": ["非常顺畅", "顺畅", "一般", "不顺畅", "很不顺畅"],
            "is_required": True
        },
        {
            "text": "您希望团队在哪些方面有所改进？",
            "type": "text_input",
            "is_required": False
        }
    ]
    
    for i, question_data in enumerate(questions_14):
        try:
            print(f"   添加问题 {i+1}: {question_data['text'][:30]}...")
            response = requests.post(f"{BASE_URL}/surveys/{survey_id}/questions/", json=question_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ 问题 {i+1} 添加成功")
            else:
                print(f"   ❌ 问题 {i+1} 添加失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ 问题 {i+1} 添加异常: {str(e)}")
    
    print("\n🎉 问题添加完成!")

if __name__ == "__main__":
    main()
