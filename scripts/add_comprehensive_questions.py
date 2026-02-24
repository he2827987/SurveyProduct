#!/usr/bin/env python3
"""
综合问题添加脚本 - 为数据库添加所有类型的问题，创建者ID为2
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# 创建者ID为2的问题数据
CREATOR_ID = 2

# 综合问题数据，包含所有类型
COMPREHENSIVE_QUESTIONS = [
    # 单选题 (SINGLE_CHOICE)
    {
        "text": "您对当前的工作环境满意度如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "非常满意", "score": 5},
            {"text": "满意", "score": 4},
            {"text": "一般", "score": 3},
            {"text": "不满意", "score": 2},
            {"text": "非常不满意", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 5,
        "tags": ["工作环境", "满意度"],
        "category": "工作环境"
    },
    {
        "text": "您认为公司的薪资待遇如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "很有竞争力", "score": 5},
            {"text": "有竞争力", "score": 4},
            {"text": "一般", "score": 3},
            {"text": "偏低", "score": 2},
            {"text": "很低", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 5,
        "tags": ["薪资", "福利"],
        "category": "薪资福利"
    },
    
    # 多选题 (MULTI_CHOICE)
    {
        "text": "您认为公司需要改进的方面有哪些？（可多选）",
        "type": "MULTI_CHOICE",
        "options": [
            {"text": "工作环境", "score": 1},
            {"text": "薪资福利", "score": 1},
            {"text": "培训机会", "score": 1},
            {"text": "晋升机制", "score": 1},
            {"text": "团队协作", "score": 1},
            {"text": "工作压力", "score": 1},
            {"text": "其他", "score": 1}
        ],
        "is_required": False,
        "min_score": 0,
        "max_score": 7,
        "tags": ["改进建议", "多选"],
        "category": "改进建议"
    },
    {
        "text": "您希望获得哪些技能培训？（可多选）",
        "type": "MULTI_CHOICE",
        "options": [
            {"text": "技术技能", "score": 1},
            {"text": "管理技能", "score": 1},
            {"text": "沟通技能", "score": 1},
            {"text": "领导力", "score": 1},
            {"text": "项目管理", "score": 1},
            {"text": "时间管理", "score": 1}
        ],
        "is_required": False,
        "min_score": 0,
        "max_score": 6,
        "tags": ["培训", "技能发展"],
        "category": "培训发展"
    },
    
    # 文本输入题 (TEXT_INPUT)
    {
        "text": "您对公司有什么建议或意见？",
        "type": "TEXT_INPUT",
        "options": [],
        "is_required": False,
        "min_score": 0,
        "max_score": 0,
        "tags": ["建议", "文本输入"],
        "category": "建议反馈"
    },
    {
        "text": "请描述您工作中遇到的主要挑战",
        "type": "TEXT_INPUT",
        "options": [],
        "is_required": False,
        "min_score": 0,
        "max_score": 0,
        "tags": ["挑战", "工作情况"],
        "category": "工作情况"
    },
    
    # 数字输入题 (NUMBER_INPUT)
    {
        "text": "您在公司工作了多少年？",
        "type": "NUMBER_INPUT",
        "options": [],
        "is_required": True,
        "min_score": 0,
        "max_score": 0,
        "tags": ["工作年限", "基本信息"],
        "category": "基本信息"
    },
    {
        "text": "您当前团队的规模是多少人？",
        "type": "NUMBER_INPUT",
        "options": [],
        "is_required": True,
        "min_score": 0,
        "max_score": 0,
        "tags": ["团队规模", "组织架构"],
        "category": "组织架构"
    },
    
    # 排序题 (模拟使用多选题形式)
    {
        "text": "请按重要性排序以下工作要素（1为最重要）",
        "type": "MULTI_CHOICE",
        "options": [
            {"text": "薪资待遇", "score": 3},
            {"text": "工作环境", "score": 2},
            {"text": "发展机会", "score": 1},
            {"text": "工作生活平衡", "score": 0}
        ],
        "is_required": True,
        "min_score": 0,
        "max_score": 6,
        "tags": ["工作价值观", "排序"],
        "category": "价值观"
    },
    
    # 关联题 - 父题
    {
        "text": "您使用公司的IT系统频率如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "每天使用", "score": 4},
            {"text": "每周几次", "score": 3},
            {"text": "偶尔使用", "score": 2},
            {"text": "很少使用", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 4,
        "tags": ["IT系统", "使用频率"],
        "category": "IT系统"
    },
    # 关联题 - 子题
    {
        "text": "您认为IT系统需要改进哪些功能？",
        "type": "MULTI_CHOICE",
        "options": [
            {"text": "界面设计", "score": 1},
            {"text": "响应速度", "score": 1},
            {"text": "功能完整性", "score": 1},
            {"text": "易用性", "score": 1},
            {"text": "稳定性", "score": 1}
        ],
        "is_required": False,
        "min_score": 0,
        "max_score": 5,
        "tags": ["IT系统", "改进建议"],
        "category": "IT系统"
    },
    
    # 更多满意度相关问题
    {
        "text": "您对团队的协作氛围满意度如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "非常满意", "score": 5},
            {"text": "满意", "score": 4},
            {"text": "一般", "score": 3},
            {"text": "不满意", "score": 2},
            {"text": "非常不满意", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 5,
        "tags": ["团队协作", "满意度"],
        "category": "团队协作"
    },
    
    # 发展机会相关问题
    {
        "text": "您对公司的晋升机会满意度如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "非常满意", "score": 5},
            {"text": "满意", "score": 4},
            {"text": "一般", "score": 3},
            {"text": "不满意", "score": 2},
            {"text": "非常不满意", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 5,
        "tags": ["晋升机会", "职业发展"],
        "category": "职业发展"
    },
    
    # 工作生活平衡
    {
        "text": "您的工作生活平衡状况如何？",
        "type": "SINGLE_CHOICE",
        "options": [
            {"text": "非常好", "score": 5},
            {"text": "较好", "score": 4},
            {"text": "一般", "score": 3},
            {"text": "较差", "score": 2},
            {"text": "很差", "score": 1}
        ],
        "is_required": True,
        "min_score": 1,
        "max_score": 5,
        "tags": ["工作生活平衡", "生活质量"],
        "category": "工作生活"
    }
]

def login_as_creator():
    """以创建者ID=2的身份登录"""
    print(f"🔐 尝试以用户ID {CREATOR_ID}身份登录...")
    
    # 首先获取所有用户信息
    try:
        # 使用管理员登录获取用户列表
        admin_login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/users/login/access-token", data=admin_login_data)
        if response.status_code != 200:
            print(f"❌ 管理员登录失败: {response.status_code} - {response.text}")
            return None
            
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取用户列表
        response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
        if response.status_code != 200:
            print(f"❌ 获取用户列表失败: {response.status_code}")
            return None
            
        users = response.json()
        creator_user = None
        for user in users:
            if user.get('id') == CREATOR_ID:
                creator_user = user
                break
                
        if not creator_user:
            print(f"❌ 未找到ID为 {CREATOR_ID} 的用户")
            # 创建新用户
            user_data = {
                "username": f"user_{CREATOR_ID}",
                "email": f"user_{CREATOR_ID}@example.com",
                "password": "password123",
                "role": "user"
            }
            response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=admin_headers)
            if response.status_code in [200, 201]:
                creator_user = response.json()
                print(f"✅ 创建新用户成功，ID: {creator_user['id']}")
            else:
                print(f"❌ 创建用户失败: {response.status_code} - {response.text}")
                return None
                
        # 尝试直接使用用户ID登录
        login_data = {
            "username": creator_user['username'],
            "password": "password123"  # 如果是创建的用户
        }
        
        response = requests.post(f"{BASE_URL}/users/login/access-token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ 用户 {creator_user['username']} 登录成功")
            return token
        else:
            print(f"❌ 用户登录失败: {response.status_code} - {response.text}")
            # 使用管理员token继续
            return admin_token
            
    except Exception as e:
        print(f"❌ 登录过程异常: {str(e)}")
        return None

def create_or_get_tags(headers, tag_names):
    """创建或获取标签"""
    tag_ids = []
    for tag_name in tag_names:
        try:
            # 检查标签是否已存在
            response = requests.get(f"{BASE_URL}/tags/", headers=headers)
            if response.status_code == 200:
                existing_tags = response.json()
                for tag in existing_tags:
                    if tag.get('name') == tag_name:
                        tag_ids.append(tag['id'])
                        print(f"   ✅ 标签 '{tag_name}' 已存在，ID: {tag['id']}")
                        break
                else:
                    # 创建新标签
                    tag_data = {
                        "name": tag_name,
                        "color": "#409EFF",
                        "description": f"标签: {tag_name}"
                    }
                    response = requests.post(f"{BASE_URL}/tags/", json=tag_data, headers=headers)
                    if response.status_code in [200, 201]:
                        new_tag = response.json()
                        tag_ids.append(new_tag['id'])
                        print(f"   ✅ 创建标签 '{tag_name}' 成功，ID: {new_tag['id']}")
                    else:
                        print(f"   ❌ 创建标签 '{tag_name}' 失败: {response.status_code}")
            else:
                print(f"   ❌ 获取标签列表失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 处理标签 '{tag_name}' 异常: {str(e)}")
    
    return tag_ids

def create_or_get_category(headers, category_name):
    """创建或获取分类"""
    try:
        # 检查分类是否已存在
        response = requests.get(f"{BASE_URL}/categories/", headers=headers)
        if response.status_code == 200:
            existing_categories = response.json()
            for category in existing_categories:
                if category.get('name') == category_name:
                    print(f"   ✅ 分类 '{category_name}' 已存在，ID: {category['id']}")
                    return category['id']
            
            # 创建新分类
            category_data = {
                "name": category_name,
                "description": f"分类: {category_name}",
                "code": category_name.lower().replace(" ", "_")
            }
            response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=headers)
            if response.status_code in [200, 201]:
                new_category = response.json()
                print(f"   ✅ 创建分类 '{category_name}' 成功，ID: {new_category['id']}")
                return new_category['id']
            else:
                print(f"   ❌ 创建分类 '{category_name}' 失败: {response.status_code}")
                return None
        else:
            print(f"   ❌ 获取分类列表失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ 处理分类 '{category_name}' 异常: {str(e)}")
        return None

def create_question(headers, question_data):
    """创建问题"""
    try:
        print(f"   ➕ 创建问题: {question_data['text'][:50]}...")
        
        # 处理选项
        options_json = None
        if question_data['options']:
            options_json = json.dumps(question_data['options'])
        
        # 创建问题数据
        question_payload = {
            "text": question_data['text'],
            "type": question_data['type'],
            "options": options_json,
            "is_required": question_data['is_required'],
            "owner_id": CREATOR_ID,
            "min_score": question_data['min_score'],
            "max_score": question_data['max_score']
        }
        
        response = requests.post(f"{BASE_URL}/questions/", json=question_payload, headers=headers)
        if response.status_code in [200, 201]:
            created_question = response.json()
            question_id = created_question['id']
            print(f"   ✅ 问题创建成功，ID: {question_id}")
            
            # 处理标签关联
            if question_data.get('tags'):
                tag_ids = create_or_get_tags(headers, question_data['tags'])
                for tag_id in tag_ids:
                    try:
                        tag_response = requests.post(
                            f"{BASE_URL}/questions/{question_id}/tags/{tag_id}", 
                            headers=headers
                        )
                        if tag_response.status_code in [200, 201]:
                            print(f"      ✅ 关联标签成功，Tag ID: {tag_id}")
                        else:
                            print(f"      ❌ 关联标签失败: {tag_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ 关联标签异常: {str(e)}")
            
            # 处理分类
            if question_data.get('category'):
                category_id = create_or_get_category(headers, question_data['category'])
                if category_id:
                    try:
                        category_response = requests.put(
                            f"{BASE_URL}/questions/{question_id}/category/{category_id}",
                            headers=headers
                        )
                        if category_response.status_code in [200, 201]:
                            print(f"      ✅ 设置分类成功，Category ID: {category_id}")
                        else:
                            print(f"      ❌ 设置分类失败: {category_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ 设置分类异常: {str(e)}")
            
            return question_id
        else:
            print(f"   ❌ 问题创建失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 创建问题异常: {str(e)}")
        return None

def create_survey_and_add_questions(headers):
    """创建调研并添加问题"""
    try:
        # 创建调研
        survey_data = {
            "title": "综合员工满意度调研",
            "description": "这是一份综合性的员工满意度调研，包含工作环境、薪资福利、团队协作等多个维度的调查",
            "created_by_user_id": CREATOR_ID
        }
        
        response = requests.post(f"{BASE_URL}/surveys/", json=survey_data, headers=headers)
        if response.status_code in [200, 201]:
            survey = response.json()
            survey_id = survey['id']
            print(f"✅ 调研创建成功，ID: {survey_id}")
            
            # 为调研添加问题
            for i, question_data in enumerate(COMPREHENSIVE_QUESTIONS):
                question_id = create_question(headers, question_data)
                if question_id:
                    # 将问题添加到调研
                    survey_question_data = {
                        "survey_id": survey_id,
                        "question_id": question_id,
                        "order": i + 1
                    }
                    
                    try:
                        response = requests.post(f"{BASE_URL}/surveys/{survey_id}/questions/", 
                                               json={"question_id": question_id, "order": i + 1}, 
                                               headers=headers)
                        if response.status_code in [200, 201]:
                            print(f"      ✅ 问题添加到调研成功")
                        else:
                            print(f"      ❌ 问题添加到调研失败: {response.status_code}")
                    except Exception as e:
                        print(f"      ❌ 添加问题到调研异常: {str(e)}")
            
            return survey_id
        else:
            print(f"❌ 调研创建失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建调研异常: {str(e)}")
        return None

def main():
    """主函数"""
    print("🚀 综合问题添加脚本")
    print("=" * 60)
    print(f"创建者ID: {CREATOR_ID}")
    print(f"问题数量: {len(COMPREHENSIVE_QUESTIONS)}")
    print("=" * 60)
    
    # 登录
    token = login_as_creator()
    if not token:
        print("❌ 无法登录，脚本终止")
        sys.exit(1)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建调研并添加问题
    survey_id = create_survey_and_add_questions(headers)
    
    if survey_id:
        print("\n" + "=" * 60)
        print("🎉 综合问题添加完成!")
        print(f"调研ID: {survey_id}")
        print(f"添加的问题数量: {len(COMPREHENSIVE_QUESTIONS)}")
        print("包含的问题类型:")
        print("  - 单选题 (SINGLE_CHOICE)")
        print("  - 多选题 (MULTI_CHOICE)")
        print("  - 文本输入题 (TEXT_INPUT)")
        print("  - 数字输入题 (NUMBER_INPUT)")
        print("  - 排序题 (模拟实现)")
        print("  - 关联题 (父子关系)")
        print("=" * 60)
    else:
        print("❌ 调研创建失败")
        sys.exit(1)

if __name__ == "__main__":
    main()