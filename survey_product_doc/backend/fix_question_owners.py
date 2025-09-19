#!/usr/bin/env python3
"""
修复题目创建者ID的脚本
将所有题目的创建者都设置为caibijuhao用户
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.models.question import Question
from backend.app.models.user import User

def fix_question_owners():
    """将所有题目的创建者都设置为caibijuhao用户"""
    db = SessionLocal()
    try:
        # 查找caibijuhao用户
        caibijuhao_user = db.query(User).filter(User.username == 'CaibiJuhao').first()
        if not caibijuhao_user:
            print("错误：数据库中没有找到用户 'CaibiJuhao'")
            return
        
        print(f"使用用户 '{caibijuhao_user.username}' (ID: {caibijuhao_user.id}) 作为所有题目的创建者")
        
        # 查找所有全局题库题目（survey_id为NULL的题目）
        all_questions = db.query(Question).filter(
            Question.survey_id.is_(None)
        ).all()
        
        if not all_questions:
            print("没有找到需要修复的题目")
            return
        
        print(f"找到 {len(all_questions)} 个题目需要设置创建者")
        
        # 更新所有题目的创建者
        updated_count = 0
        for question in all_questions:
            if question.owner_id != caibijuhao_user.id:
                question.owner_id = caibijuhao_user.id
                updated_count += 1
                print(f"设置题目 ID {question.id}: '{question.text[:30]}...' 的创建者为 {caibijuhao_user.username}")
        
        # 提交更改
        db.commit()
        print(f"成功更新了 {updated_count} 个题目的创建者")
        
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始修复题目创建者ID...")
    fix_question_owners()
    print("修复完成！")
