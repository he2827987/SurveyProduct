#!/usr/bin/env python3
"""
测试调研创建时题目关联功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import engine
from backend.app.services.survey_service import create_survey
from backend.app.schemas.survey import SurveyCreate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def test_survey_creation_with_questions():
    """测试调研创建时是否正确关联题目"""

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        try:
            print("🧪 测试调研创建时题目关联功能")

            # 创建包含question_ids的调研
            survey_data = SurveyCreate(
                title='测试调研-题目关联修复验证',
                description='验证create_survey函数是否正确处理question_ids',
                question_ids=[36, 38, 74]  # 使用实际存在的题目ID
            )

            print(f"📝 创建调研数据: {survey_data.title}")
            print(f"📋 选择的题目ID: {survey_data.question_ids}")

            # 创建调研（使用用户ID=2）
            new_survey = create_survey(db, survey_data, user_id=2)

            print(f"✅ 调研创建成功，ID: {new_survey.id}")

            # 检查关联表
            result = db.execute(text(f'SELECT * FROM survey_questions WHERE survey_id = {new_survey.id} ORDER BY `order`'))
            associations = result.fetchall()

            print(f"🔗 找到 {len(associations)} 条关联记录:")

            if len(associations) == 3:
                for i, assoc in enumerate(associations, 1):
                    survey_id, question_id, order_val = assoc[1], assoc[2], assoc[3]
                    print(f"  {i}. 调研ID: {survey_id}, 题目ID: {question_id}, 顺序: {order_val}")

                    # 获取题目信息
                    q_result = db.execute(text(f'SELECT text FROM questions WHERE id = {question_id}'))
                    q_row = q_result.fetchone()
                    if q_row:
                        print(f"     题目内容: {q_row[0][:50]}...")

                print("🎉 测试通过！题目关联功能正常工作")

                # 测试API调用
                test_api_call(new_survey.id)

                return True
            else:
                print(f"❌ 期望3条关联记录，但实际找到{len(associations)}条")
                return False

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_api_call(survey_id):
    """测试API调用是否能正确获取题目"""
    try:
        import requests

        # 注意：这里需要有效的token，暂时跳过API测试
        print("📡 API测试跳过（需要有效token）")

        # 直接查询数据库验证
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM survey_questions WHERE survey_id = {survey_id}'))
            count = result.fetchone()[0]
            print(f"📊 数据库验证: 调研 {survey_id} 有 {count} 个题目")

    except ImportError:
        print("📡 requests库不可用，跳过API测试")
    except Exception as e:
        print(f"📡 API测试失败: {e}")

if __name__ == "__main__":
    success = test_survey_creation_with_questions()
    sys.exit(0 if success else 1)
