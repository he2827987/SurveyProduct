#!/usr/bin/env python3
"""
模拟线上环境题目创建问题的诊断脚本
"""

import sys
import os

# 先设置环境变量
os.environ.setdefault('OPENROUTER_API_KEY', 'dummy_key_for_testing')
os.environ.setdefault('SECRET_KEY', 'dummy_secret_key_for_testing')
os.environ.setdefault('DATABASE_URL', 'mysql+pymysql://survey_user:heyang425070@localhost:3306/survey_db')

sys.path.append('survey_product_doc')

from sqlalchemy import text
from backend.app.database import SessionLocal, engine
from backend.app import crud, models, schemas
from backend.app.models.question import QuestionType

def test_with_production_env():
    """使用生产环境配置测试"""
    print("🧪 使用生产环境配置测试题目创建...")

    # 设置生产环境变量（模拟线上环境）
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['OPENROUTER_API_KEY'] = 'dummy_key'
    os.environ['SECRET_KEY'] = 'dummy_secret'
    os.environ['DATABASE_URL'] = 'mysql+pymysql://survey_user:heyang425070@localhost:3306/survey_db'

    # 重新加载配置模块
    import importlib
    import backend.app.config
    importlib.reload(backend.app.config)
    from backend.app.config import settings

    print(f"🗄️ 数据库URL: {settings.DATABASE_URL}")
    print(f"🔑 OPENROUTER_API_KEY: {settings.OPENROUTER_API_KEY[:10]}...")

    db = SessionLocal()
    try:
        # 测试数据库连接
        print("🔍 测试数据库连接...")
        db.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")

        # 获取现有用户
        test_user = db.query(models.User).first()
        if not test_user:
            print("❌ 未找到用户")
            return False

        print(f"👤 使用用户: {test_user.username} (ID: {test_user.id})")

        # 创建题目（模拟前端发送的数据）
        question_data = {
            "text": "线上环境测试题目",
            "type": "single_choice",
            "is_required": True,
            "options": [
                {"text": "选项A", "score": 5},
                {"text": "选项B", "score": 3}
            ],
            "tags": ["线上测试"]
        }

        print(f"📝 题目数据: {question_data}")

        # 创建Pydantic模型
        question_create = schemas.QuestionCreate(**question_data)
        print("✅ 数据验证通过")

        # 调用CRUD函数
        print("🚀 创建题目...")
        result = crud.create_global_question(
            db=db,
            question=question_create,
            owner_id=test_user.id
        )

        print(f"🎉 题目创建成功! ID: {result.id}")
        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_json_serialization():
    """测试JSON序列化问题"""
    print("🔍 测试JSON序列化...")

    import json

    test_options = [
        {"text": "选项A", "score": 5},
        {"text": "选项B", "score": 3}
    ]

    try:
        json_str = json.dumps(test_options, ensure_ascii=False)
        print(f"✅ JSON序列化成功: {json_str}")

        parsed = json.loads(json_str)
        print(f"✅ JSON解析成功: {parsed}")
        return True
    except Exception as e:
        print(f"❌ JSON序列化失败: {e}")
        return False

def test_database_constraints():
    """测试数据库约束"""
    print("🗄️ 测试数据库约束...")

    os.environ['DATABASE_URL'] = 'mysql+pymysql://survey_user:heyang425070@localhost:3306/survey_db'

    db = SessionLocal()
    try:
        # 检查questions表结构
        result = db.execute(text("""
            SELECT COLUMN_NAME, IS_NULLABLE, DATA_TYPE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'questions' AND TABLE_SCHEMA = 'survey_db'
            ORDER BY ORDINAL_POSITION
        """))

        columns = result.fetchall()
        print("📋 Questions表结构:")
        for col in columns:
            nullable = "NULL" if col[1] == "YES" else "NOT NULL"
            print(f"  {col[0]}: {col[2]} {nullable} DEFAULT {col[3]}")

        # 检查关键字段
        required_fields = ['text', 'type', 'owner_id']
        for field in required_fields:
            field_info = next((col for col in columns if col[0] == field), None)
            if field_info and field_info[1] == "NO":
                print(f"✅ 必填字段 {field}: 检查通过")
            else:
                print(f"⚠️ 字段 {field}: 可能是可选的")

        return True

    except Exception as e:
        print(f"❌ 数据库约束检查失败: {e}")
        return False
    finally:
        db.close()

def analyze_error_patterns():
    """分析可能的错误模式"""
    print("🔍 分析可能的错误模式...")

    possible_issues = [
        {
            "name": "数据库连接失败",
            "symptoms": ["Can't connect to MySQL server", "Connection refused"],
            "solution": "检查DATABASE_URL环境变量和数据库服务状态"
        },
        {
            "name": "用户认证失败",
            "symptoms": ["Invalid token", "User not found"],
            "solution": "检查JWT token和用户认证逻辑"
        },
        {
            "name": "数据验证失败",
            "symptoms": ["Validation error", "Field required"],
            "solution": "检查前端发送的数据格式和后端验证规则"
        },
        {
            "name": "数据库约束冲突",
            "symptoms": ["Duplicate entry", "Foreign key constraint fails"],
            "solution": "检查数据库表结构和外键关系"
        },
        {
            "name": "权限问题",
            "symptoms": ["Permission denied", "Access forbidden"],
            "solution": "检查用户权限和API权限控制"
        },
        {
            "name": "JSON序列化错误",
            "symptoms": ["JSON decode error", "Invalid JSON"],
            "solution": "检查options字段的JSON处理逻辑"
        }
    ]

    for issue in possible_issues:
        print(f"\n🔸 {issue['name']}:")
        print(f"   症状: {', '.join(issue['symptoms'])}")
        print(f"   解决方案: {issue['solution']}")

if __name__ == "__main__":
    print("=" * 70)
    print("🔬 线上环境题目创建问题诊断")
    print("=" * 70)

    # 基础测试
    print("\n1️⃣ JSON序列化测试:")
    test_json_serialization()

    print("\n2️⃣ 数据库约束检查:")
    test_database_constraints()

    print("\n3️⃣ 生产环境模拟测试:")
    test_with_production_env()

    print("\n4️⃣ 错误模式分析:")
    analyze_error_patterns()

    print("\n" + "=" * 70)
    print("📋 诊断建议:")
    print("1. 检查线上环境变量配置")
    print("2. 查看Render应用日志")
    print("3. 验证数据库连接字符串")
    print("4. 确认用户认证状态")
    print("5. 检查前端发送的数据格式")
    print("=" * 70)