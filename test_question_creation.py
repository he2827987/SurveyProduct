#!/usr/bin/env python3
"""
测试题目创建功能的脚本
用于诊断线上服务创建题目失败的问题
"""

import sys
import os
sys.path.append('survey_product_doc')

from sqlalchemy import text

# 设置环境变量
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('OPENROUTER_API_KEY', 'dummy_key_for_testing')
os.environ.setdefault('SECRET_KEY', 'dummy_secret_key_for_testing')
os.environ.setdefault('DATABASE_URL', 'mysql+pymysql://survey_user:heyang425070@localhost:3306/survey_db')

from backend.app.database import SessionLocal, engine
from backend.app import crud, models, schemas
from backend.app.models.question import QuestionType
from sqlalchemy.orm import Session

def test_create_global_question():
    """测试创建全局题目"""
    print("🧪 开始测试创建全局题目...")

    # 创建数据库会话
    db = SessionLocal()
    try:
        # 首先检查数据库连接
        print("🔍 检查数据库连接...")
        db.execute(text("SELECT 1"))
        print("✅ 数据库连接正常")

        # 使用现有用户
        print("👤 查找现有用户...")
        test_user = db.query(models.User).first()
        if not test_user:
            print("❌ 未找到任何用户")
            return False
        print(f"✅ 使用用户 ID: {test_user.id}, 用户名: {test_user.username}")

        # 测试创建题目数据
        print("📝 准备题目数据...")
        question_data = {
            "text": "这是一个测试题目",
            "type": QuestionType.SINGLE_CHOICE,
            "is_required": True,
            "options": [
                {"text": "选项A", "score": 5},
                {"text": "选项B", "score": 3},
                {"text": "选项C", "score": 1}
            ],
            "tags": ["测试", "单选题"]
        }

        print(f"📊 题目数据: {question_data}")

        # 创建Pydantic模型
        question_create = schemas.QuestionCreate(**question_data)
        print("✅ Pydantic模型创建成功")

        # 调用CRUD函数
        print("🚀 调用 create_global_question...")
        result = crud.create_global_question(
            db=db,
            question=question_create,
            owner_id=test_user.id
        )

        print(f"🎉 题目创建成功! ID: {result.id}")
        print(f"📄 题目详情: {result.text}")
        print(f"🏷️ 标签: {[tag.name for tag in result.tags]}")

        return True

    except Exception as e:
        print(f"❌ 错误发生: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_database_tables():
    """测试数据库表是否存在"""
    print("🗄️ 检查数据库表...")

    db = SessionLocal()
    try:
        # 检查关键表
        tables_to_check = ['users', 'questions', 'tags', 'question_tags']

        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✅ 表 {table}: {count} 条记录")
            except Exception as e:
                print(f"❌ 表 {table} 检查失败: {e}")

        return True
    except Exception as e:
        print(f"❌ 数据库表检查失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 题目创建诊断脚本")
    print("=" * 60)

    # 测试数据库表
    if not test_database_tables():
        print("❌ 数据库表检查失败，退出")
        sys.exit(1)

    print()

    # 测试题目创建
    if test_create_global_question():
        print("✅ 所有测试通过")
    else:
        print("❌ 测试失败")
        sys.exit(1)

    print("=" * 60)