#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models.survey import Survey
from backend.app.models.question import Question, QuestionType
from backend.app.models.answer import SurveyAnswer
from backend.app.models.participant import Participant
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.user import User
from datetime import datetime, timedelta
import json
import random

def create_test_data():
    """创建测试数据"""
    db = SessionLocal()
    try:
        print("开始创建测试数据...")
        
        # 获取组织6
        org = db.query(Organization).filter(Organization.id == 6).first()
        if not org:
            print("组织6不存在，请先创建组织")
            return
        
        # 获取用户3
        user = db.query(User).filter(User.id == 3).first()
        if not user:
            print("用户3不存在，请先创建用户")
            return
        
        # 获取部门
        departments = db.query(Department).filter(Department.organization_id == 6).all()
        if not departments:
            print("没有找到部门，请先创建部门")
            return
        
        # 创建测试调研
        print("1. 创建测试调研...")
        survey = Survey(
            title="员工满意度调研",
            description="了解员工对工作环境、薪资待遇、团队氛围等方面的满意度",
            created_by_user_id=user.id,
            organization_id=org.id
        )
        db.add(survey)
        db.commit()
        db.refresh(survey)
        print(f"创建调研: {survey.title} (ID: {survey.id})")
        
        # 创建问题
        print("2. 创建调研问题...")
        questions_data = [
            {
                "text": "您对当前工作环境的满意度如何？",
                "type": QuestionType.SINGLE_CHOICE,
                "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"]
            },
            {
                "text": "您认为公司的薪资待遇如何？",
                "type": QuestionType.SINGLE_CHOICE,
                "options": ["很有竞争力", "有竞争力", "一般", "偏低", "很低"]
            },
            {
                "text": "您最喜欢公司的哪些方面？（可多选）",
                "type": QuestionType.MULTI_CHOICE,
                "options": ["工作环境", "团队氛围", "薪资待遇", "发展机会", "工作内容", "管理制度"]
            },
            {
                "text": "您认为公司需要改进的方面有哪些？（可多选）",
                "type": QuestionType.MULTI_CHOICE,
                "options": ["薪资待遇", "工作环境", "管理制度", "团队氛围", "发展机会", "工作内容"]
            },
            {
                "text": "您对公司的建议或意见：",
                "type": QuestionType.TEXT_INPUT,
                "options": []
            },
            {
                "text": "您在公司工作了多少年？",
                "type": QuestionType.NUMBER_INPUT,
                "options": []
            }
        ]
        
        questions = []
        for q_data in questions_data:
            question = Question(
                text=q_data["text"],
                type=q_data["type"],
                options=json.dumps(q_data["options"]),
                survey_id=survey.id,
                order=len(questions) + 1
            )
            db.add(question)
            questions.append(question)
        
        db.commit()
        for q in questions:
            db.refresh(q)
        print(f"创建了 {len(questions)} 个问题")
        
        # 创建参与者
        print("3. 创建测试参与者...")
        participants_data = [
            {"name": "张三", "position": "软件工程师", "department_id": departments[0].id if departments else None},
            {"name": "李四", "position": "产品经理", "department_id": departments[0].id if departments else None},
            {"name": "王五", "position": "UI设计师", "department_id": departments[0].id if departments else None},
            {"name": "赵六", "position": "测试工程师", "department_id": departments[1].id if len(departments) > 1 else None},
            {"name": "钱七", "position": "项目经理", "department_id": departments[1].id if len(departments) > 1 else None},
            {"name": "孙八", "position": "运维工程师", "department_id": departments[0].id if departments else None},
            {"name": "周九", "position": "数据分析师", "department_id": departments[1].id if len(departments) > 1 else None},
            {"name": "吴十", "position": "前端工程师", "department_id": departments[0].id if departments else None},
        ]
        
        participants = []
        for p_data in participants_data:
            participant = Participant(
                name=p_data["name"],
                position=p_data["position"],
                department_id=p_data["department_id"],
                organization_id=org.id
            )
            db.add(participant)
            participants.append(participant)
        
        db.commit()
        for p in participants:
            db.refresh(p)
        print(f"创建了 {len(participants)} 个参与者")
        
        # 创建答案
        print("4. 创建测试答案...")
        answers_count = 0
        
        # 为每个参与者创建答案
        for participant in participants:
            # 随机决定是否参与（80%参与率）
            if random.random() < 0.8:
                # 创建答案数据
                answer_data = {}
                
                for question in questions:
                    if question.type == QuestionType.SINGLE_CHOICE:
                        options = json.loads(question.options)
                        answer_data[str(question.id)] = random.choice(options)
                    
                    elif question.type == QuestionType.MULTI_CHOICE:
                        options = json.loads(question.options)
                        # 随机选择1-3个选项
                        num_choices = random.randint(1, min(3, len(options)))
                        selected_options = random.sample(options, num_choices)
                        answer_data[str(question.id)] = selected_options
                    
                    elif question.type == QuestionType.TEXT_INPUT:
                        if "建议" in question.text:
                            suggestions = [
                                "希望增加培训机会",
                                "建议改善办公环境",
                                "希望能有更多团队活动",
                                "建议优化工作流程",
                                "希望增加福利待遇"
                            ]
                            answer_data[str(question.id)] = random.choice(suggestions)
                        else:
                            answer_data[str(question.id)] = "这是一个测试回答"
                    
                    elif question.type == QuestionType.NUMBER_INPUT:
                        answer_data[str(question.id)] = random.randint(1, 10)
                
                # 创建答案记录
                answer = SurveyAnswer(
                    survey_id=survey.id,
                    participant_id=participant.id,
                    answers=json.dumps(answer_data),
                    submitted_at=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(answer)
                answers_count += 1
        
        db.commit()
        print(f"创建了 {answers_count} 个答案")
        
        print("测试数据创建完成！")
        print(f"调研ID: {survey.id}")
        print(f"问题数量: {len(questions)}")
        print(f"参与者数量: {len(participants)}")
        print(f"答案数量: {answers_count}")
        
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
