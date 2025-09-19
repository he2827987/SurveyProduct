#!/usr/bin/env python3
"""
测试LLM API的脚本
"""
import requests
import json

def test_llm_api():
    """测试LLM API是否正常工作"""
    
    # API基础URL
    base_url = "http://localhost:8000/api/v1"
    
    # 测试数据
    test_data = {
        "survey_data": {
            "survey_title": "员工满意度调研",
            "total_answers": 100,
            "question_analytics": [
                {
                    "question_text": "您对工作环境的满意度如何？",
                    "question_type": "single_choice",
                    "total_responses": 100,
                    "response_distribution": {
                        "非常满意": 30,
                        "满意": 40,
                        "一般": 20,
                        "不满意": 8,
                        "非常不满意": 2
                    }
                }
            ],
            "participant_analysis": {
                "total_participants": 100,
                "by_department": {
                    "技术部": 45,
                    "市场部": 30,
                    "人事部": 25
                },
                "by_position": {
                    "员工": 70,
                    "主管": 20,
                    "经理": 10
                }
            },
            "participation_rate": 85.5
        }
    }
    
    try:
        # 发送请求
        response = requests.post(
            f"{base_url}/llm/generate_survey_summary",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM API 测试成功!")
            print(f"生成的总结: {result.get('summary', '无总结')[:200]}...")
        else:
            print(f"❌ LLM API 测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("开始测试LLM API...")
    test_llm_api()
