import json
import random
from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.models.survey import Survey
from backend.app.models.question import Question, QuestionType
from backend.app.models.survey_question import SurveyQuestion
from backend.app.models.answer import SurveyAnswer

# 配置
SURVEY_TITLE = "模拟问卷 - 部门职务测试"
CREATED_BY_USER_ID = 2  # 如有需要可改为实际用户 ID
QUESTION_COUNT = 10
ANSWER_COUNT = 100

departments = ["技术部", "产品部", "运营部", "市场部", "人事部", "财务部"]
positions = ["executive", "manager", "senior", "junior", "intern"]

# 预设题目（10 道）
QUESTION_DEFS = [
    # 单选题（带分值）
    {"text": "Q1: 对产品满意度？", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "非常满意", "score": 10}, {"text": "满意", "score": 8},
                 {"text": "一般", "score": 6}, {"text": "不满意", "score": 3}]},
    {"text": "Q2: 对团队合作评价？", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "优秀", "score": 10}, {"text": "良好", "score": 8},
                 {"text": "一般", "score": 6}, {"text": "较差", "score": 3}]},
    {"text": "Q3: 对工作环境评价？", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "很好", "score": 9}, {"text": "还行", "score": 7},
                 {"text": "一般", "score": 5}, {"text": "较差", "score": 2}]},
    # 多选题（带分值）
    {"text": "Q4: 你认为哪些福利重要？", "type": QuestionType.MULTI_CHOICE,
     "options": [{"text": "薪资", "score": 5}, {"text": "保险", "score": 4},
                 {"text": "弹性工作", "score": 3}, {"text": "培训", "score": 2}]},
    {"text": "Q5: 你最关注的职业发展要素？", "type": QuestionType.MULTI_CHOICE,
     "options": [{"text": "晋升", "score": 5}, {"text": "学习机会", "score": 4},
                 {"text": "项目挑战", "score": 3}, {"text": "领导支持", "score": 2}]},
    # 填空题（无分值）
    {"text": "Q6: 对公司改进的建议？", "type": QuestionType.TEXT_INPUT, "options": None},
    {"text": "Q7: 你最想学习的技能？", "type": QuestionType.TEXT_INPUT, "options": None},
    # 再加 3 题混合
    {"text": "Q8: 对绩效考核认可度？", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "认可", "score": 8}, {"text": "基本认可", "score": 6},
                 {"text": "一般", "score": 4}, {"text": "不认可", "score": 2}]},
    {"text": "Q9: 你更看重的激励？", "type": QuestionType.MULTI_CHOICE,
     "options": [{"text": "奖金", "score": 4}, {"text": "期权", "score": 4},
                 {"text": "表彰", "score": 2}, {"text": "休假", "score": 3}]},
    {"text": "Q10: 目前最大的工作痛点？", "type": QuestionType.TEXT_INPUT, "options": None},
]

def build_option_map(opts):
    if not opts:
        return {}
    return {o["text"]: o.get("score", 0) for o in opts}

def calc_score_for_answer(q_def, ans_value):
    if q_def["type"] == QuestionType.SINGLE_CHOICE:
        opt_map = build_option_map(q_def["options"])
        return opt_map.get(ans_value, 0)
    if q_def["type"] == QuestionType.MULTI_CHOICE:
        opt_map = build_option_map(q_def["options"])
        return sum(opt_map.get(v, 0) for v in ans_value) if isinstance(ans_value, list) else 0
    return 0  # 文本题不给分

def main():
    session = SessionLocal()
    try:
        # 若已有同名问卷则删除旧记录（可按需注释）
        existing = session.query(Survey).filter(Survey.title == SURVEY_TITLE).first()
        if existing:
            # 级联删除答案/关联的题，简单起见直接删除问卷及关联
            session.query(SurveyAnswer).filter(SurveyAnswer.survey_id == existing.id).delete()
            session.query(SurveyQuestion).filter(SurveyQuestion.survey_id == existing.id).delete()
            session.delete(existing)
            session.commit()

        # 创建问卷
        survey = Survey(
            title=SURVEY_TITLE,
            description="模拟数据问卷，用于图表与分析测试",
            created_by_user_id=CREATED_BY_USER_ID
        )
        session.add(survey)
        session.commit()
        session.refresh(survey)

        # 创建题目并关联
        questions = []
        for idx, qd in enumerate(QUESTION_DEFS, start=1):
            q = Question(
                text=qd["text"],
                type=qd["type"],
                options=json.dumps(qd["options"], ensure_ascii=False) if qd["options"] else None,
                category_id=None,
                is_required=False,
                order=idx,
                owner_id=CREATED_BY_USER_ID,
            )
            session.add(q)
            session.commit()
            session.refresh(q)
            questions.append(q)
            # 建立问卷关联
            session.add(SurveyQuestion(survey_id=survey.id, question_id=q.id, order=idx))
        session.commit()

        # 为便于评分，构建题目定义 map
        qdef_map = {str(q.id): QUESTION_DEFS[i] for i, q in enumerate(questions)}

        # 生成回答
        for _ in range(ANSWER_COUNT):
            dept = random.choice(departments)
            pos = random.choice(positions)
            answers_dict = {}
            total_score = 0.0

            for q in questions:
                qid_str = str(q.id)
                qdef = qdef_map[qid_str]
                qtype = qdef["type"]

                if qtype == QuestionType.SINGLE_CHOICE:
                    opt = random.choice(qdef["options"])
                    answers_dict[qid_str] = opt["text"]
                    total_score += calc_score_for_answer(qdef, opt["text"])
                elif qtype == QuestionType.MULTI_CHOICE:
                    # 随机 1~2 个选项
                    opts = random.sample(qdef["options"], k=random.randint(1, 2))
                    val_list = [o["text"] for o in opts]
                    answers_dict[qid_str] = val_list
                    total_score += calc_score_for_answer(qdef, val_list)
                else:
                    # 文本题
                    answers_dict[qid_str] = f"自由回答 {random.randint(1, 100)}"
                    # 不计分

            sa = SurveyAnswer(
                survey_id=survey.id,
                answers=json.dumps(answers_dict, ensure_ascii=False),
                department=dept,
                position=pos,
                total_score=int(total_score)
            )
            session.add(sa)

        session.commit()
        print(f"Seed done: survey_id={survey.id}, questions={len(questions)}, answers={ANSWER_COUNT}")
    finally:
        session.close()

if __name__ == "__main__":
    main()