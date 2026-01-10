#!/usr/bin/env python3
"""
题目CRUD功能测试脚本
测试题目的创建、读取、更新、删除功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json
import argparse

def test_question_crud(cleanup_after_test=False):
    """测试题目CRUD功能"""
    base_url = "http://localhost:8000"
    
    print("📝 题目CRUD功能测试")
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
    
    # 2. 测试创建单选题
    print("2. 测试创建单选题...")
    print("-" * 30)
    
    single_choice_data = {
        "text": "您对当前工作环境的满意度如何？",
        "type": "single_choice",
        "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"],
        "is_required": True
    }
    
    response = requests.post(f"{base_url}/api/v1/questions/", 
                           headers=headers, json=single_choice_data)
    if response.status_code in [200, 201]:
        single_question = response.json()
        print(f"✅ 创建单选题成功: {single_question['text']} (ID: {single_question['id']})")
    else:
        print(f"❌ 创建单选题失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return
    
    print()
    
    # 3. 测试创建多选题
    print("3. 测试创建多选题...")
    print("-" * 30)
    
    multi_choice_data = {
        "text": "您最喜欢公司的哪些方面？（可多选）",
        "type": "multi_choice",
        "options": ["工作环境", "团队氛围", "薪资待遇", "发展机会", "工作内容"],
        "is_required": False
    }
    
    response = requests.post(f"{base_url}/api/v1/questions/", 
                           headers=headers, json=multi_choice_data)
    if response.status_code in [200, 201]:
        multi_question = response.json()
        print(f"✅ 创建多选题成功: {multi_question['text']} (ID: {multi_question['id']})")
    else:
        print(f"❌ 创建多选题失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 4. 测试创建填空题
    print("4. 测试创建填空题...")
    print("-" * 30)
    
    text_input_data = {
        "text": "您对公司的建议或意见：",
        "type": "text_input",
        "is_required": False
    }
    
    response = requests.post(f"{base_url}/api/v1/questions/", 
                           headers=headers, json=text_input_data)
    if response.status_code in [200, 201]:
        text_question = response.json()
        print(f"✅ 创建填空题成功: {text_question['text']} (ID: {text_question['id']})")
    else:
        print(f"❌ 创建填空题失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 5. 测试创建数字题
    print("5. 测试创建数字题...")
    print("-" * 30)
    
    number_input_data = {
        "text": "您在公司工作了多少年？",
        "type": "number_input",
        "is_required": True
    }
    
    response = requests.post(f"{base_url}/api/v1/questions/", 
                           headers=headers, json=number_input_data)
    if response.status_code in [200, 201]:
        number_question = response.json()
        print(f"✅ 创建数字题成功: {number_question['text']} (ID: {number_question['id']})")
    else:
        print(f"❌ 创建数字题失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 6. 测试获取题目列表
    print("6. 测试获取题目列表...")
    print("-" * 30)
    
    response = requests.get(f"{base_url}/api/v1/questions/", headers=headers)
    if response.status_code == 200:
        questions_data = response.json()
        print(f"✅ 获取题目列表成功，共 {questions_data.get('total', 0)} 个题目:")
        for question in questions_data.get('items', []):
            print(f"   - {question['text']} (ID: {question['id']}, 类型: {question['type']})")
    else:
        print(f"❌ 获取题目列表失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 7. 测试更新题目
    print("7. 测试更新题目...")
    print("-" * 30)
    
    if 'single_question' in locals():
        update_data = {
            "text": "您对当前工作环境的满意度如何？（已更新）",
            "options": ["非常满意", "满意", "一般", "不满意", "非常不满意", "无法评价"]
        }
        
        response = requests.put(f"{base_url}/api/v1/questions/{single_question['id']}", 
                              headers=headers, json=update_data)
        if response.status_code == 200:
            updated_question = response.json()
            print(f"✅ 更新题目成功:")
            print(f"   新标题: {updated_question['text']}")
            print(f"   选项数: {len(updated_question['options'])}")
        else:
            print(f"❌ 更新题目失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print()
    
    # 8. 测试按类型筛选题目
    print("8. 测试按类型筛选题目...")
    print("-" * 30)
    
    # 筛选单选题
    response = requests.get(f"{base_url}/api/v1/questions/?type=single_choice", headers=headers)
    if response.status_code == 200:
        single_questions = response.json()
        print(f"✅ 获取单选题成功，共 {single_questions.get('total', 0)} 个单选题")
    else:
        print(f"❌ 获取单选题失败: {response.status_code}")
    
    # 筛选填空题
    response = requests.get(f"{base_url}/api/v1/questions/?type=text_input", headers=headers)
    if response.status_code == 200:
        text_questions = response.json()
        print(f"✅ 获取填空题成功，共 {text_questions.get('total', 0)} 个填空题")
    else:
        print(f"❌ 获取填空题失败: {response.status_code}")
    
    print()
    
    # 9. 测试删除题目（可选）
    print("9. 测试删除题目...")
    print("-" * 30)
    
    # 注意：这里不实际删除，因为可能还有其他测试需要使用
    print("⚠️  跳过删除测试，避免影响其他功能")
    
    print()
    print("🎉 题目CRUD功能测试完成！")
    print("=" * 50)
    
    # 10. 清理测试题目（可选）
    if cleanup_after_test:
        print("\n🧹 清理测试题目...")
        print("-" * 30)
        
        # 定义测试题目的特征文本
        test_question_texts = [
            "您对当前工作环境的满意度如何？",
            "您最喜欢公司的哪些方面？（可多选）",
            "您对公司的建议或意见：",
            "您在公司工作了多少年？",
            "您对当前工作环境的满意度如何？（已更新）",
            "您对当前工作环境满意吗？"
        ]
        
        # 删除测试题目
        deleted_count = 0
        for text in test_question_texts:
            response = requests.get(f"{base_url}/api/v1/questions/?search={text}", headers=headers)
            if response.status_code == 200:
                questions_data = response.json()
                for question in questions_data.get('items', []):
                    if any(test_text in question['text'] for test_text in test_question_texts):
                        delete_response = requests.delete(f"{base_url}/api/v1/questions/{question['id']}", headers=headers)
                        if delete_response.status_code == 200:
                            deleted_count += 1
                            print(f"删除测试题目: {question['text'][:50]}...")
        
        print(f"✅ 清理完成，删除了 {deleted_count} 个测试题目")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='题目CRUD功能测试')
    parser.add_argument('--cleanup', action='store_true', help='测试完成后自动清理测试题目')
    args = parser.parse_args()
    
    test_question_crud(cleanup_after_test=args.cleanup)
