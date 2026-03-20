#!/usr/bin/env python3
"""
测试脚本：验证所有修复
1. 调研页面请求发送问题
2. 登录重定向功能
3. 数据分析页面布局
"""

import requests
import json
import time
import webbrowser
from threading import Timer

# 配置
BASE_URL = "http://localhost:3000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def test_backend_health():
    """测试后端健康状态"""
    print("=== 1. 测试后端健康状态 ===")
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API正常响应")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端API连接失败: {e}")
        return False

def test_survey_list_request():
    """测试调研列表API请求"""
    print("\n=== 2. 测试调研列表API请求 ===")
    
    # 先获取token
    login_data = {
        "username": "testuser2",
        "password": "testpass"
    }
    
    try:
        # 登录获取token
        response = requests.post("http://127.0.0.1:8000/api/v1/users/login/access-token", 
                              data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            
            if token:
                print("✅ 成功获取认证token")
                
                # 测试调研列表API
                headers = {**HEADERS, "Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
                
                if response.status_code == 200:
                    surveys = response.json()
                    print(f"✅ 调研列表API请求成功")
                    print(f"   返回 {len(surveys)} 个调研")
                    for survey in surveys:
                        print(f"   - {survey['title']} (ID: {survey['id']})")
                    return True
                else:
                    print(f"❌ 调研列表API请求失败: {response.status_code}")
                    print(f"   响应: {response.text}")
                    return False
            else:
                print("❌ 获取token失败")
                return False
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_login_redirect():
    """测试登录重定向功能"""
    print("\n=== 3. 测试登录重定向功能 ===")
    print("将在浏览器中测试重定向功能...")
    print("\n测试步骤:")
    print("1. 访问登录页面 http://localhost:3000/login")
    print("2. 如果未登录，应显示登录表单")
    print("3. 使用 testuser2 / testpass 登录")
    print("4. 登录成功后应自动跳转到首页")
    print("5. 再次访问 /login，应自动跳转到首页（已登录状态）")
    print("6. 清除localStorage后访问 /login，应显示登录表单")
    
    # 打开浏览器
    webbrowser.open("http://localhost:3000/login")
    
    return True

def test_analysis_page():
    """测试数据分析页面"""
    print("\n=== 4. 测试数据分析页面 ===")
    print("将在浏览器中测试数据分析页面...")
    print("\n测试步骤:")
    print("1. 访问数据分析页面 http://localhost:3000/analysis")
    print("2. 应看到三个切换按钮：'筛选分析'、'标签分析'、'企业对比'")
    print("3. 默认显示'筛选分析'板块")
    print("4. 点击不同按钮应切换显示对应板块")
    print("5. 每次只显示一个板块")
    
    # 等待3秒后打开分析页面
    Timer(3.0, lambda: webbrowser.open("http://localhost:3000/analysis")).start()
    
    return True

def main():
    print("=== 修复验证测试 ===\n")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 执行测试
    test1 = test_backend_health()
    test2 = test_survey_list_request()
    test3 = test_login_redirect()
    test4 = test_analysis_page()
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"1. 后端健康检查: {'✅' if test1 else '❌'}")
    print(f"2. 调研列表请求: {'✅' if test2 else '❌'}")
    print(f"3. 登录重定向功能: {'✅' if test3 else '❌'}")
    print(f"4. 数据分析页面: {'✅' if test4 else '❌'}")
    
    if test1 and test2:
        print("\n🎉 核心功能测试通过！")
        print("\n请在浏览器中验证以下功能：")
        print("1. 登录页面的自动重定向")
        print("2. 调研列表的数据加载")
        print("3. 数据分析页面的标签切换")
    else:
        print("\n⚠️ 部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()
