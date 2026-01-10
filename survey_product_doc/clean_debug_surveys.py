#!/usr/bin/env python3
"""
清除数据库中的调试调研
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("🧹 清除数据库中的调试调研")
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
    
    # 2. 获取所有调研
    print("\n📋 获取所有调研...")
    response = requests.get(f"{BASE_URL}/surveys/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取调研列表失败: {response.status_code} - {response.text}")
        return
    
    surveys = response.json()
    print(f"✅ 获取到 {len(surveys)} 个调研")
    
    # 3. 识别调试调研
    debug_surveys = []
    normal_surveys = []
    
    for survey in surveys:
        title = survey.get('title', '')
        if '调试' in title or '测试' in title:
            debug_surveys.append(survey)
        else:
            normal_surveys.append(survey)
    
    print(f"\n🔍 调研分类:")
    print(f"   - 总调研数: {len(surveys)}")
    print(f"   - 调试调研数: {len(debug_surveys)}")
    print(f"   - 正常调研数: {len(normal_surveys)}")
    
    if not debug_surveys:
        print("\n✅ 没有发现调试调研，无需清理")
        return
    
    # 4. 显示要删除的调试调研
    print(f"\n🚨 将要删除的调试调研:")
    for survey in debug_surveys:
        print(f"   - ID: {survey['id']}, 标题: {survey['title']}")
    
    # 5. 确认删除
    print(f"\n⚠️  警告: 此操作将永久删除 {len(debug_surveys)} 个调试调研!")
    confirm = input("确认删除? (输入 'yes' 确认): ")
    
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    # 6. 删除调试调研
    print(f"\n🗑️  开始删除调试调研...")
    deleted_count = 0
    failed_count = 0
    
    for survey in debug_surveys:
        survey_id = survey['id']
        survey_title = survey['title']
        
        print(f"   正在删除: ID={survey_id}, 标题={survey_title}")
        
        try:
            response = requests.delete(f"{BASE_URL}/surveys/{survey_id}", headers=headers)
            
            if response.status_code in [200, 204]:
                print(f"   ✅ 删除成功: ID={survey_id}")
                deleted_count += 1
            else:
                print(f"   ❌ 删除失败: ID={survey_id}, 状态码={response.status_code}")
                failed_count += 1
                
        except Exception as e:
            print(f"   ❌ 删除异常: ID={survey_id}, 错误={str(e)}")
            failed_count += 1
    
    # 7. 显示删除结果
    print(f"\n📊 删除结果:")
    print(f"   - 成功删除: {deleted_count} 个")
    print(f"   - 删除失败: {failed_count} 个")
    print(f"   - 剩余正常调研: {len(normal_surveys)} 个")
    
    if deleted_count > 0:
        print(f"\n✅ 调试调研清理完成!")
        
        # 显示剩余的正常调研
        print(f"\n📋 剩余的正常调研:")
        for survey in normal_surveys:
            print(f"   - ID: {survey['id']}, 标题: {survey['title']}")
    else:
        print(f"\n❌ 没有成功删除任何调研")

if __name__ == "__main__":
    main()

