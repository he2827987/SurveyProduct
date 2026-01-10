#!/usr/bin/env python3
import requests
import json
import time

def test_llm_summary():
    """测试LLM自动总结功能"""
    base_url = "http://localhost:8000"
    
    print("🤖 LLM自动总结功能测试")
    print("=" * 50)
    
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
    
    # 2. 测试调研AI总结
    print("2. 测试调研AI总结...")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics/ai-summary", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 调研AI总结生成成功")
        print(f"📝 调研标题: {data['survey_title']}")
        print(f"📊 总答案数: {data['total_answers']}")
        print(f"📈 参与率: {data.get('participation_rate', 0):.1f}%")
        print(f"⏰ 生成时间: {data['generated_at']}")
        print(f"📋 关键指标: {data['key_metrics']}")
        print()
        print("🤖 AI总结内容:")
        print("-" * 30)
        print(data['summary'])
        print()
    else:
        print(f"❌ 调研AI总结生成失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return
    
    # 3. 测试问题AI洞察
    print("3. 测试问题AI洞察...")
    print("-" * 30)
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/questions/35/ai-insights", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ 问题AI洞察生成成功")
        print(f"❓ 问题: {data['question_text']}")
        print(f"📊 回答数: {data['total_responses']}")
        print(f"⏰ 分析时间: {data['analysis_timestamp']}")
        print()
        print("🤖 AI洞察内容:")
        print("-" * 30)
        print(data['insights'])
        print()
    else:
        print(f"❌ 问题AI洞察生成失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 4. 测试LLM直接API
    print("4. 测试LLM直接API...")
    print("-" * 30)
    
    # 获取调研数据用于测试
    survey_response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics", headers=headers)
    if survey_response.status_code == 200:
        survey_data = survey_response.json()
        
        # 测试生成调研总结
        llm_request = {
            "survey_data": survey_data
        }
        
        response = requests.post(f"{base_url}/api/v1/llm/generate_survey_summary", 
                               headers=headers, json=llm_request)
        if response.status_code == 200:
            data = response.json()
            print("✅ LLM直接API调研总结生成成功")
            print(f"📝 调研标题: {data['survey_title']}")
            print(f"📊 总答案数: {data['total_answers']}")
            print(f"⏰ 生成时间: {data['generated_at']}")
            print()
            print("🤖 LLM总结内容预览:")
            print("-" * 30)
            summary_preview = data['summary'][:500] + "..." if len(data['summary']) > 500 else data['summary']
            print(summary_preview)
            print()
        else:
            print(f"❌ LLM直接API调研总结生成失败: {response.status_code}")
            print(f"   响应: {response.text}")
        
        # 测试生成问题洞察
        if survey_data['question_analytics']:
            question_data = survey_data['question_analytics'][0]
            llm_request = {
                "question_data": question_data
            }
            
            response = requests.post(f"{base_url}/api/v1/llm/generate_question_insights", 
                                   headers=headers, json=llm_request)
            if response.status_code == 200:
                data = response.json()
                print("✅ LLM直接API问题洞察生成成功")
                print(f"❓ 问题: {data['question_text']}")
                print(f"📊 回答数: {data['total_responses']}")
                print(f"⏰ 分析时间: {data['analysis_timestamp']}")
                print()
                print("🤖 LLM洞察内容预览:")
                print("-" * 30)
                insights_preview = data['insights'][:500] + "..." if len(data['insights']) > 500 else data['insights']
                print(insights_preview)
                print()
            else:
                print(f"❌ LLM直接API问题洞察生成失败: {response.status_code}")
                print(f"   响应: {response.text}")
    
    # 5. 性能测试
    print("5. 性能测试...")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.get(f"{base_url}/api/v1/organizations/6/surveys/1/analytics/ai-summary", headers=headers)
    end_time = time.time()
    
    if response.status_code == 200:
        print(f"✅ AI总结生成耗时: {end_time - start_time:.2f} 秒")
    else:
        print(f"❌ 性能测试失败: {response.status_code}")
    
    print()
    print("🎉 LLM自动总结功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_llm_summary()
