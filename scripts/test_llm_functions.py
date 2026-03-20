#!/usr/bin/env python3
"""
简化的LLM功能测试脚本
专门测试标签分析和总结生成功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_llm_tag_analysis():
    """测试LLM标签分析功能"""
    print("\n🔍 测试LLM标签分析功能")
    print("=" * 50)
    
    try:
        # 测试获取标签列表
        response = requests.get(f"{BASE_URL}/tags/")
        
        if response.status_code != 200:
            print(f"❌ 获取标签列表失败: {response.status_code}")
            return False
        
        tags = response.json()
        print(f"✅ 获取到 {len(tags)} 个标签")
        
        # 模拟标签分析请求
        analysis_data = {
            "analysis_request": {
                "tag_id": 1,
                "analysis_type": "tag_summary",
                "data": {
                    "tag_id": 1,
                    "tag_name": "工作环境",
                    "tag_color": "#409EFF",
                    "question_count": 8,
                    "total_score": 420
                }
            }
        }
        
        print(f"📊 发送LLM标签分析请求...")
        
        response = requests.post(f"{BASE_URL}/llm/tag-analysis", json=analysis_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM标签分析成功")
            print(f"   结果类型: {result.get('type', '无')}")
            print(f"   回复长度: {len(result.get('result', [])} 字符}")
            return True
        else:
            print(f"❌ LLM标签分析失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LLM标签分析异常: {str(e)}")
        return False

def test_llm_survey_insights():
    """测试LLM调研洞察功能"""
    print("\n🔍 测试LLM调研洞察功能")
    print("=" * 50)
    
    try:
        # 测试获取调研列表
        response = requests.get(f"{BASE_URL}/surveys/")
        
        if response.status_code != 200:
            print(f"❌ 获取调研列表失败: {response.status_code}")
            return False
        
        surveys = response.json()
        if len(surveys) == 0:
            print("⚠️ 暂无调研数据")
            return False
            
        # 使用第一个调研进行测试
        test_survey = surveys[0]
        print(f"📋 使用调研: {test_survey['title']} (ID: {test_survey['id']})")
        
        insights_data = {
            "insights_request": {
                "survey_id": test_survey['id'],
                "analysis_type": "survey_insights",
                "data": {
                    "survey_id": test_survey['id'],
                    "survey_title": test_survey['title'],
                    "participant_count": 25,
                    "response_count": 20
                    "completion_rate": 80
                    "analysis_type": "participant_analysis"
                }
            }
        }
        
        print(f"📊 发送LLM调研洞察请求...")
        
        response = requests.post(f"{BASE_URL}/llm/survey-insights", json=insights_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM调研洞察成功")
            print(f"   洞察结果: {result.get('insight', '无类型')}")
            if 'insight' in result:
                insights = result['insight']
                print(f"   洞察结果: {len(insights)} 条")
                for insight in insights[:3]:
                    print(f"   - {insight.get('insight', '无类型')}")
            return True
        else:
            print(f"❌ LLM调研洞察失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LLM调研洞察异常: {str(e)}")
        return False

def test_llm_summary():
    """测试LLM总结生成功能"""
    print("\n🔍 测试LLM总结生成功能")
    print("=" * 50)
    
    try:
        # 测试获取调研列表
        response = requests.get(f"{BASE_URL}/surveys/")
        
        if response.status_code != 200:
            print(f"❌ 获取调研列表失败: {response.status_code}")
            return False
        
        surveys = response.json()
        if len(surveys) == 0:
            print("⚠️ 暂无调研数据")
            return False
        
        # 使用第一个调研进行测试
        test_survey = surveys[0]
        summary_request = {
            "summary_request": {
                "survey_id": test_survey['id'],
                "analysis_type": "comprehensive_summary",
                "data": {
                    "survey_id": test_survey['id'],
                    "survey_title": test_survey['title'],
                    "total_participants": 25,
                    "completion_rate": 80
                    "analysis_type": "comprehensive_summary"
                }
            }
        }
        
        print(f"📊 发送LLM总结请求...")
        
        response = requests.post(f"{BASE_URL}/llm/generate-survey-summary", json=summary_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM总结生成成功")
            print(f"   生成的总结长度: {len(result.get('summary', '')} 字符")
            return True
        else:
            print(f"❌ LLM总结生成失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LLM总结生成异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始LLM功能全面测试")
    print("=" * 60)
    
    all_tests = [
        ("LLM标签分析", test_llm_tag_analysis),
        ("LLM调研洞察", test_llm_survey_insights),
        ("LLM总结生成", test_llm_summary)
    ]
    
    results = {
        "LLM标签分析": False,
        "LLM调研洞察": False,
        "LLM总结生成": False
    }
    
    for test_name, test_func in all_tests:
        print(f"\n🔍 执行: {test_name}")
        results[test_name] = test_func()
        print(f"   状态: {'✅' if results[test_name] else '❌'}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试总结:")
    print(f"   - LLM标签分析: {results['LLM标签分析']}")
    print(f"   - LLM调研洞察: {results['LLM调研洞察']}")
    print(f"   - LLM总结生成: {results['LLM总结生成']}")
    print(f"   - 总成功率: {sum(results.values()) / len(all_tests) * 100:.1f}%")
    
    # 关闭浏览器
    print("\n🔧 清理资源...")
    return results

if __name__main__":
    main()