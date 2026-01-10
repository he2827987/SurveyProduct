#!/usr/bin/env python3
"""
测试运行脚本
用于快速运行各种测试
"""
import os
import sys
import subprocess
import argparse

def run_test(test_path, cleanup=False):
    """运行指定的测试文件"""
    try:
        cmd = [sys.executable, test_path]
        if cleanup and "test_question_crud.py" in test_path:
            cmd.append("--cleanup")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {test_path} - 通过")
            return True
        else:
            print(f"❌ {test_path} - 失败")
            print(f"   错误: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_path} - 超时")
        return False
    except Exception as e:
        print(f"💥 {test_path} - 异常: {e}")
        return False

def run_demo_tests():
    """运行演示测试"""
    print("🎯 运行演示测试...")
    demos = [
        "demo_analytics.py",
        "demo_llm_summary.py"
    ]
    
    success_count = 0
    for demo in demos:
        if run_test(demo):
            success_count += 1
    
    return success_count, len(demos)

def run_api_tests():
    """运行API测试"""
    print("\n🔌 运行API测试...")
    api_tests = [
        "api/test_login.py",
        "api/test_new_apis.py",
        "api/test_api_simple.py"
    ]
    
    success_count = 0
    for test in api_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(api_tests)

def run_analytics_tests():
    """运行数据分析测试"""
    print("\n📊 运行数据分析测试...")
    analytics_tests = [
        "analytics/test_analytics_api.py",
        "analytics/test_advanced_analytics.py"
    ]
    
    success_count = 0
    for test in analytics_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(analytics_tests)

def run_llm_tests():
    """运行LLM功能测试"""
    print("\n🤖 运行LLM功能测试...")
    llm_tests = [
        "llm/test_llm_simple.py"
    ]
    
    success_count = 0
    for test in llm_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(llm_tests)

def run_organization_tests():
    """运行组织管理测试"""
    print("\n🏢 运行组织管理测试...")
    org_tests = [
        "organization/test_org_simple.py",
        "organization/test_org.py"
    ]
    
    success_count = 0
    for test in org_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(org_tests)

def run_department_tests():
    """运行部门管理测试"""
    print("\n📁 运行部门管理测试...")
    dept_tests = [
        "department/test_department_simple.py",
        "department/test_department_api.py"
    ]
    
    success_count = 0
    for test in dept_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(dept_tests)

def run_category_tests():
    """运行分类管理测试"""
    print("\n🏷️ 运行分类管理测试...")
    category_tests = [
        "category/test_category_api.py"
    ]
    
    success_count = 0
    for test in category_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(category_tests)

def run_question_tests(cleanup=False):
    """运行题目管理测试"""
    print("\n📝 运行题目管理测试...")
    question_tests = [
        "question/test_question_crud.py",
        "question/test_question_search.py",
        "question/test_frontend_search.py",
        "question/test_question_sorting.py"
    ]
    
    success_count = 0
    for test in question_tests:
        if run_test(test, cleanup=cleanup):
            success_count += 1
    
    return success_count, len(question_tests)

def run_utils_tests():
    """运行工具测试"""
    print("\n🔧 运行工具测试...")
    utils_tests = [
        "utils/test_db.py",
        "utils/create_test_data.py"
    ]
    
    success_count = 0
    for test in utils_tests:
        if run_test(test):
            success_count += 1
    
    return success_count, len(utils_tests)

def main():
    parser = argparse.ArgumentParser(description="运行调研平台测试")
    parser.add_argument("--demo", action="store_true", help="运行演示测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--analytics", action="store_true", help="运行数据分析测试")
    parser.add_argument("--llm", action="store_true", help="运行LLM功能测试")
    parser.add_argument("--organization", action="store_true", help="运行组织管理测试")
    parser.add_argument("--department", action="store_true", help="运行部门管理测试")
    parser.add_argument("--category", action="store_true", help="运行分类管理测试")
    parser.add_argument("--question", action="store_true", help="运行题目管理测试")
    parser.add_argument("--utils", action="store_true", help="运行工具测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--cleanup", action="store_true", help="测试完成后自动清理测试题目")
    
    args = parser.parse_args()
    
    print("🚀 调研平台测试运行器")
    print("=" * 50)
    
    total_success = 0
    total_tests = 0
    
    # 根据参数运行相应的测试
    if args.all or args.demo:
        success, count = run_demo_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.api:
        success, count = run_api_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.analytics:
        success, count = run_analytics_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.llm:
        success, count = run_llm_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.organization:
        success, count = run_organization_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.department:
        success, count = run_department_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.category:
        success, count = run_category_tests()
        total_success += success
        total_tests += count
    
    if args.all or args.question:
        success, count = run_question_tests(cleanup=args.cleanup)
        total_success += success
        total_tests += count
    
    if args.all or args.utils:
        success, count = run_utils_tests()
        total_success += success
        total_tests += count
    
    # 如果没有指定任何参数，显示帮助信息
    if not any([args.demo, args.api, args.analytics, args.llm, 
                args.organization, args.department, args.category, args.question, args.utils, args.all]):
        print("请指定要运行的测试类型，或使用 --all 运行所有测试")
        print("可用的测试类型:")
        print("  --demo        运行演示测试")
        print("  --api         运行API测试")
        print("  --analytics   运行数据分析测试")
        print("  --llm         运行LLM功能测试")
        print("  --organization 运行组织管理测试")
        print("  --department  运行部门管理测试")
        print("  --category    运行分类管理测试")
        print("  --question    运行题目管理测试")
        print("  --utils       运行工具测试")
        print("  --all         运行所有测试")
        print("  --cleanup     测试完成后自动清理测试题目（仅对题目测试有效）")
        return 0
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {total_success}/{total_tests} 通过")
    
    if total_success == total_tests:
        print("🎉 所有测试通过！")
        return 0
    else:
        print(f"⚠️  有 {total_tests - total_success} 个测试失败")
        return 1

if __name__ == "__main__":
    # 切换到tests目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
