#!/usr/bin/env python3
"""
测试企业对比AI分析功能的脚本
"""
import requests
import json
import os

# 手动加载.env文件
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"')

load_env()

def test_enterprise_comparison_ai():
    """测试企业对比AI分析端点"""
    
    # API基础URL
    base_url = "http://localhost:8000/api/v1"
    
    # 测试参数
    organization_id = 2
    survey_id = 20
    
    # 模拟企业对比数据
    comparison_data = {
        "dimension": "question",
        "companies": [
            {"id": 1, "name": "企业A"},
            {"id": 2, "name": "企业B"},
            {"id": 3, "name": "企业C"}
        ],
        "comparison_data": [
            {
                "organization_name": "企业A",
                "average_score": 85.5,
                "participation_rate": 92.3,
                "average_satisfaction": 4.2
            },
            {
                "organization_name": "企业B", 
                "average_score": 78.2,
                "participation_rate": 88.7,
                "average_satisfaction": 3.8
            },
            {
                "organization_name": "企业C",
                "average_score": 91.8,
                "participation_rate": 95.1,
                "average_satisfaction": 4.5
            }
        ]
    }
    
    try:
        print(f"测试企业对比AI分析端点: /organizations/{organization_id}/surveys/{survey_id}/analytics/enterprise-comparison-ai")
        print(f"对比数据: {json.dumps(comparison_data, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        response = requests.post(
            f"{base_url}/organizations/{organization_id}/surveys/{survey_id}/analytics/enterprise-comparison-ai",
            headers={"Content-Type": "application/json"},
            json=comparison_data,
            timeout=300
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 企业对比AI分析端点测试成功!")
            print(f"调研标题: {result.get('survey_title', '未知')}")
            print(f"生成时间: {result.get('generated_at', '未知')}")
            print(f"AI分析内容: {result.get('comparison_analysis', '无分析')[:300]}...")
        else:
            print(f"❌ 企业对比AI分析端点测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("开始测试企业对比AI分析功能...")
    test_enterprise_comparison_ai()
