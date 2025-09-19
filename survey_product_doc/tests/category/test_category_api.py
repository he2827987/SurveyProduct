#!/usr/bin/env python3
"""
分类API测试脚本
测试分类的增删改查功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json

def test_category_api():
    """测试分类API功能"""
    base_url = "http://localhost:8000"
    
    print("🏷️ 分类API功能测试")
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
    
    # 2. 测试创建分类
    print("2. 测试创建分类...")
    print("-" * 30)
    
    # 创建顶级分类
    category_data = {
        "name": "员工满意度调研",
        "description": "用于评估员工对工作各方面的满意度",
        "code": "EMP_SAT",
        "sort_order": 1,
        "is_active": True
    }
    
    response = requests.post(f"{base_url}/api/v1/categories", 
                           headers=headers, json=category_data)
    if response.status_code == 200:
        category1 = response.json()
        print(f"✅ 创建顶级分类成功: {category1['name']} (ID: {category1['id']})")
    else:
        print(f"❌ 创建顶级分类失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return
    
    # 创建子分类
    sub_category_data = {
        "name": "工作环境",
        "description": "工作环境相关的满意度调查",
        "code": "WORK_ENV",
        "parent_id": category1['id'],
        "sort_order": 1,
        "is_active": True
    }
    
    response = requests.post(f"{base_url}/api/v1/categories", 
                           headers=headers, json=sub_category_data)
    if response.status_code == 200:
        category2 = response.json()
        print(f"✅ 创建子分类成功: {category2['name']} (ID: {category2['id']})")
    else:
        print(f"❌ 创建子分类失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    # 创建另一个顶级分类
    category_data2 = {
        "name": "产品反馈",
        "description": "产品相关的反馈和建议",
        "code": "PROD_FEED",
        "sort_order": 2,
        "is_active": True
    }
    
    response = requests.post(f"{base_url}/api/v1/categories", 
                           headers=headers, json=category_data2)
    if response.status_code == 200:
        category3 = response.json()
        print(f"✅ 创建第二个顶级分类成功: {category3['name']} (ID: {category3['id']})")
    else:
        print(f"❌ 创建第二个顶级分类失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 3. 测试获取分类列表
    print("3. 测试获取分类列表...")
    print("-" * 30)
    
    response = requests.get(f"{base_url}/api/v1/categories", headers=headers)
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ 获取分类列表成功，共 {len(categories)} 个分类:")
        for cat in categories:
            print(f"   - {cat['name']} (ID: {cat['id']}, 题目数: {cat['question_count']})")
    else:
        print(f"❌ 获取分类列表失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 4. 测试获取分类树
    print("4. 测试获取分类树...")
    print("-" * 30)
    
    response = requests.get(f"{base_url}/api/v1/categories/tree", headers=headers)
    if response.status_code == 200:
        tree = response.json()
        print(f"✅ 获取分类树成功，共 {len(tree)} 个顶级分类:")
        
        def print_tree(categories, level=0):
            for cat in categories:
                indent = "  " * level
                print(f"{indent}- {cat['name']} (ID: {cat['id']}, 题目数: {cat['question_count']})")
                if cat['children']:
                    print_tree(cat['children'], level + 1)
        
        print_tree(tree)
    else:
        print(f"❌ 获取分类树失败: {response.status_code}")
        print(f"   响应: {response.text}")
    
    print()
    
    # 5. 测试获取分类详情
    print("5. 测试获取分类详情...")
    print("-" * 30)
    
    if 'category1' in locals():
        response = requests.get(f"{base_url}/api/v1/categories/{category1['id']}", headers=headers)
        if response.status_code == 200:
            category_detail = response.json()
            print(f"✅ 获取分类详情成功:")
            print(f"   名称: {category_detail['name']}")
            print(f"   描述: {category_detail['description']}")
            print(f"   层级: {category_detail['level']}")
            print(f"   路径: {category_detail['path']}")
            print(f"   子分类数: {len(category_detail['children'])}")
            print(f"   题目数: {category_detail['question_count']}")
        else:
            print(f"❌ 获取分类详情失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print()
    
    # 6. 测试更新分类
    print("6. 测试更新分类...")
    print("-" * 30)
    
    if 'category2' in locals():
        update_data = {
            "name": "工作环境与氛围",
            "description": "更新后的描述：工作环境和团队氛围相关的满意度调查"
        }
        
        response = requests.put(f"{base_url}/api/v1/categories/{category2['id']}", 
                              headers=headers, json=update_data)
        if response.status_code == 200:
            updated_category = response.json()
            print(f"✅ 更新分类成功:")
            print(f"   新名称: {updated_category['name']}")
            print(f"   新描述: {updated_category['description']}")
        else:
            print(f"❌ 更新分类失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print()
    
    # 7. 测试移动分类
    print("7. 测试移动分类...")
    print("-" * 30)
    
    if 'category2' in locals() and 'category3' in locals():
        move_data = {
            "target_parent_id": category3['id'],
            "position": 1
        }
        
        response = requests.post(f"{base_url}/api/v1/categories/{category2['id']}/move", 
                               headers=headers, json=move_data)
        if response.status_code == 200:
            print(f"✅ 移动分类成功: {category2['name']} 移动到 {category3['name']} 下")
        else:
            print(f"❌ 移动分类失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print()
    
    # 8. 测试获取子分类
    print("8. 测试获取子分类...")
    print("-" * 30)
    
    if 'category1' in locals():
        response = requests.get(f"{base_url}/api/v1/categories/{category1['id']}/children", headers=headers)
        if response.status_code == 200:
            children = response.json()
            print(f"✅ 获取子分类成功，共 {len(children)} 个子分类:")
            for child in children:
                print(f"   - {child['name']} (ID: {child['id']}, 题目数: {child['question_count']})")
        else:
            print(f"❌ 获取子分类失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print()
    
    # 9. 测试删除分类（可选）
    print("9. 测试删除分类...")
    print("-" * 30)
    
    # 注意：这里不实际删除，因为可能还有其他测试需要使用
    print("⚠️  跳过删除测试，避免影响其他功能")
    
    print()
    print("🎉 分类API功能测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_category_api()
