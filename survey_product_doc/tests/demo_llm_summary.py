#!/usr/bin/env python3
import requests
import json
import time

def demo_llm_summary():
    """演示LLM自动总结功能"""
    base_url = "http://localhost:8000"
    
    print("🤖 LLM自动总结功能演示")
    print("=" * 60)
    
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
    print("✅ 登录成功")
    print()
    
    # 2. 演示问题生成功能
    print("🎯 2. 智能问题生成演示")
    print("-" * 40)
    
    topics = [
        "员工满意度调研",
        "产品用户体验调研", 
        "团队协作效率调研"
    ]
    
    for topic in topics:
        print(f"📝 生成主题: {topic}")
        test_request = {
            "topic": topic,
            "num_questions": 2
        }
        
        response = requests.post(f"{base_url}/api/v1/llm/generate_questions", 
                               headers=headers, json=test_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功生成 {len(data['questions'])} 个问题:")
            for i, question in enumerate(data['questions'], 1):
                print(f"   {i}. {question}")
        else:
            print(f"❌ 生成失败: {response.status_code}")
        print()
    
    # 3. 演示回答总结功能
    print("📊 3. 智能回答总结演示")
    print("-" * 40)
    
    # 模拟不同类型的回答数据
    test_cases = [
        {
            "question": "您对当前工作环境的满意度如何？",
            "answers": ["非常满意", "满意", "满意", "一般", "不满意", "非常不满意", "满意"]
        },
        {
            "question": "您认为公司最需要改进的方面是什么？",
            "answers": [
                "希望增加培训机会",
                "建议改善办公环境", 
                "希望能有更多团队活动",
                "建议优化工作流程",
                "希望增加福利待遇",
                "建议改善办公环境"
            ]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"📋 测试案例 {i}: {case['question']}")
        test_request = {
            "question_text": case['question'],
            "answers": case['answers']
        }
        
        response = requests.post(f"{base_url}/api/v1/llm/summarize_answers", 
                               headers=headers, json=test_request)
        if response.status_code == 200:
            data = response.json()
            print("✅ 智能总结:")
            print(f"   {data['summary'][:200]}...")
        else:
            print(f"❌ 总结失败: {response.status_code}")
        print()
    
    # 4. 演示调研数据分析
    print("📈 4. 调研数据分析演示")
    print("-" * 40)
    
    # 获取调研数据
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics", headers=headers)
    if response.status_code == 200:
        survey_data = response.json()
        print(f"📝 调研标题: {survey_data['survey_title']}")
        print(f"📊 总答案数: {survey_data['total_answers']}")
        print(f"❓ 问题数量: {len(survey_data['question_analytics'])}")
        
        # 显示问题分析
        for i, question in enumerate(survey_data['question_analytics'][:2], 1):
            print(f"\n❓ 问题{i}: {question['question_text']}")
            print(f"   回答数: {question['total_responses']}")
            print(f"   回答分布: {question['response_distribution']}")
    else:
        print(f"❌ 获取调研数据失败: {response.status_code}")
    
    print()
    
    # 5. 演示LLM直接API调用
    print("🔧 5. LLM直接API调用演示")
    print("-" * 40)
    
    # 构造简化的调研数据用于LLM分析
    simple_survey_data = {
        "survey_title": "员工满意度调研",
        "total_answers": 7,
        "question_analytics": [
            {
                "question_text": "您对当前工作环境的满意度如何？",
                "question_type": "single_choice",
                "total_responses": 7,
                "response_distribution": {
                    "不满意": 2,
                    "一般": 1,
                    "非常满意": 2,
                    "非常不满意": 2
                }
            }
        ],
        "participant_analysis": {
            "total_participants": 7,
            "by_department": {"研发部": 5, "测试部门": 2},
            "by_position": {"软件工程师": 1, "产品经理": 1}
        }
    }
    
    print("📊 使用LLM分析调研数据...")
    llm_request = {
        "survey_data": simple_survey_data
    }
    
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/llm/generate_survey_summary", 
                           headers=headers, json=llm_request)
    end_time = time.time()
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ LLM分析完成 (耗时: {end_time - start_time:.2f}秒)")
        print(f"📝 调研标题: {data['survey_title']}")
        print(f"📊 总答案数: {data['total_answers']}")
        print(f"📋 关键指标: {data['key_metrics']}")
        print()
        print("🤖 AI生成的总结报告:")
        print("-" * 40)
        summary_preview = data['summary'][:800] + "..." if len(data['summary']) > 800 else data['summary']
        print(summary_preview)
    else:
        print(f"❌ LLM分析失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 6. 功能总结
    print("🎯 6. LLM自动总结功能总结")
    print("-" * 40)
    
    print("✅ 已实现的功能:")
    print("   📝 智能问题生成 - 根据主题自动生成调研问题")
    print("   📊 智能回答总结 - 对问题回答进行深度分析")
    print("   🤖 调研报告生成 - 自动生成专业的调研总结报告")
    print("   🔍 问题洞察分析 - 对单个问题进行深度洞察")
    print("   ⚡ 高性能处理 - 支持大规模数据分析")
    print()
    
    print("🚀 应用场景:")
    print("   📈 调研设计 - 快速生成专业调研问题")
    print("   📊 数据分析 - 自动分析调研结果")
    print("   📋 报告生成 - 生成标准化的调研报告")
    print("   🎯 决策支持 - 提供数据驱动的决策建议")
    print("   📱 实时分析 - 支持实时数据洞察")
    
    print()
    print("🎉 LLM自动总结功能演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    demo_llm_summary()
