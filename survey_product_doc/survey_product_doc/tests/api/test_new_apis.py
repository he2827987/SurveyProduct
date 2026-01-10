#!/usr/bin/env python3
"""
测试新的API功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录获取token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def test_create_organization(token):
    """测试创建组织"""
    headers = {"Authorization": f"Bearer {token}"}
    import time
    org_data = {
        "name": f"测试组织_{int(time.time())}",
        "description": "这是一个测试组织"
    }
    
    response = requests.post(f"{BASE_URL}/organizations/", json=org_data, headers=headers)
    if response.status_code in [200, 201]:
        org = response.json()
        print(f"创建组织成功: {org['name']} (ID: {org['id']})")
        return org["id"]
    else:
        print(f"创建组织失败: {response.status_code} - {response.text}")
        return None

def test_create_department(token, org_id):
    """测试创建部门"""
    headers = {"Authorization": f"Bearer {token}"}
    dept_data = {
        "name": "研发部",
        "code": "RD",
        "description": "负责产品研发"
    }
    
    response = requests.post(f"{BASE_URL}/organizations/{org_id}/departments", json=dept_data, headers=headers)
    if response.status_code == 200:
        dept = response.json()
        print(f"创建部门成功: {dept['name']} (ID: {dept['id']})")
        return dept["id"]
    else:
        print(f"创建部门失败: {response.status_code} - {response.text}")
        return None

def test_create_organization_question(token, org_id):
    """测试创建组织题库问题"""
    headers = {"Authorization": f"Bearer {token}"}
    question_data = {
        "text": "您对当前工作环境满意吗？",
        "type": "single_choice",
        "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"],
        "is_required": True
    }
    
    response = requests.post(f"{BASE_URL}/organizations/{org_id}/questions/", json=question_data, headers=headers)
    if response.status_code == 201:
        question = response.json()
        print(f"创建组织问题成功: {question['text']} (ID: {question['id']})")
        return question["id"]
    else:
        print(f"创建组织问题失败: {response.status_code} - {response.text}")
        return None

def test_create_participant(token, org_id):
    """测试创建参与者"""
    headers = {"Authorization": f"Bearer {token}"}
    participant_data = {
        "name": "张三",
        "position": "软件工程师",
        "email": "zhangsan@example.com",
        "phone": "13800000001",
        "organization_id": org_id
    }
    
    response = requests.post(f"{BASE_URL}/organizations/{org_id}/participants", json=participant_data, headers=headers)
    if response.status_code == 200:
        participant = response.json()
        print(f"创建参与者成功: {participant['name']} (ID: {participant['id']})")
        return participant["id"]
    else:
        print(f"创建参与者失败: {response.status_code} - {response.text}")
        return None

def main():
    print("=== 测试新的API功能 ===")
    
    # 1. 登录获取token
    print("\n1. 测试登录...")
    token = test_login()
    if not token:
        return
    
    # 2. 创建组织
    print("\n2. 测试创建组织...")
    org_id = test_create_organization(token)
    if not org_id:
        return
    
    # 3. 创建部门
    print("\n3. 测试创建部门...")
    dept_id = test_create_department(token, org_id)
    if not dept_id:
        return
    
    # 4. 创建组织题库问题
    print("\n4. 测试创建组织题库问题...")
    question_id = test_create_organization_question(token, org_id)
    if not question_id:
        return
    
    # 5. 创建参与者
    print("\n5. 测试创建参与者...")
    participant_id = test_create_participant(token, org_id)
    if not participant_id:
        return
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    main()
