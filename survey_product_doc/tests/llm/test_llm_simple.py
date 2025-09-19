#!/usr/bin/env python3
import requests
import json
import time

def test_llm_simple():
    """测试简化的LLM功能"""
    base_url = "http://localhost:8000"
    
    print("🤖 简化LLM功能测试")
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
    
    # 2. 测试简单的回答总结
    print("2. 测试简单的回答总结...")
    print("-" * 30)
    
    # 构造简单的测试数据
    test_request = {
        "question_text": "您对当前工作环境的满意度如何？",
        "answers": [
            "非常满意",
            "满意", 
            "一般",
            "不满意",
            "非常不满意"
        ]
    }
    
    response = requests.post(f"{base_url}/api/v1/llm/summarize_answers", 
                           headers=headers, json=test_request)
    if response.status_code == 200:
        data = response.json()
        print("✅ 简单回答总结生成成功")
        print(f"❓ 问题: {data['question_text']}")
        print()
        print("🤖 总结内容:")
        print("-" * 30)
        print(data['summary'])
        print()
    else:
        print(f"❌ 简单回答总结生成失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return
    
    # 3. 测试问题生成
    print("3. 测试问题生成...")
    print("-" * 30)
    
    test_request = {
        "topic": "员工满意度",
        "num_questions": 3
    }
    
    response = requests.post(f"{base_url}/api/v1/llm/generate_questions", 
                           headers=headers, json=test_request)
    if response.status_code == 200:
        data = response.json()
        print("✅ 问题生成成功")
        print(f"📝 主题: {test_request['topic']}")
        print(f"📊 生成问题数: {len(data['questions'])}")
        print()
        print("🤖 生成的问题:")
        print("-" * 30)
        for i, question in enumerate(data['questions'], 1):
            print(f"{i}. {question}")
        print()
    else:
        print(f"❌ 问题生成失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 4. 测试性能
    print("4. 性能测试...")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/llm/summarize_answers", 
                           headers=headers, json=test_request)
    end_time = time.time()
    
    if response.status_code == 200:
        print(f"✅ LLM调用耗时: {end_time - start_time:.2f} 秒")
    else:
        print(f"❌ 性能测试失败: {response.status_code}")
    
    print()
    print("🎉 简化LLM功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_llm_simple()
