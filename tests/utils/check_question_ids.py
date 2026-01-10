#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.question import Question
from backend.app.models.survey import Survey

def check_question_ids():
    """检查问题ID"""
    db = SessionLocal()
    try:
        print("检查调研和问题ID...")
        
        # 获取调研
        surveys = db.query(Survey).all()
        print(f"找到 {len(surveys)} 个调研:")
        for survey in surveys:
            print(f"  调研ID: {survey.id}, 标题: {survey.title}")
            
            # 获取该调研的问题
            questions = db.query(Question).filter(Question.survey_id == survey.id).all()
            print(f"    问题数量: {len(questions)}")
            for question in questions:
                print(f"      问题ID: {question.id}, 文本: {question.text[:50]}...")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_question_ids()
