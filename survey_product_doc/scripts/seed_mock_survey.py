import json
import random
from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.models.survey import Survey
from backend.app.models.question import Question, QuestionType
from backend.app.models.survey_question import SurveyQuestion
from backend.app.models.answer import SurveyAnswer
from backend.app.models.organization import Organization

SURVEY_TITLE = "模拟问卷 - 全题型覆盖"
CREATED_BY_USER_ID = 2
ANSWER_COUNT_PER_ORG = 25

QUESTION_DEFS = [
    {"key": "single", "text": "Q1: 产品满意度", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "非常满意", "score": 10}, {"text": "满意", "score": 8},
                 {"text": "一般", "score": 5}, {"text": "不满意", "score": 2}]},
    {"key": "multi", "text": "Q2: 期望的福利", "type": QuestionType.MULTI_CHOICE,
     "options": [{"text": "薪资", "score": 4}, {"text": "保险", "score": 3},
                 {"text": "弹性工作", "score": 2}, {"text": "培训", "score": 1}]},
    {"key": "text", "text": "Q3: 对公司建议", "type": QuestionType.TEXT_INPUT, "options": None},
    {"key": "number", "text": "Q4: 每周可投入加班小时", "type": QuestionType.NUMBER_INPUT, "options": None},
    {"key": "sort", "text": "Q5: 优先事项排序", "type": QuestionType.SORT_ORDER,
     "options": [{"text": "体验优化"}, {"text": "流程优化"}, {"text": "学习成长"}]},
    {"key": "cond_parent", "text": "Q6: 是否愿意参与专项项目？", "type": QuestionType.SINGLE_CHOICE,
     "options": [{"text": "愿意"}, {"text": "观望"}, {"text": "不参与"}]},
    {"key": "cond_child1", "text": "Q7: 愿意的话想负责哪块", "type": QuestionType.CONDITIONAL,
     "parent_key": "cond_parent", "trigger_options": ["愿意"]},
    {"key": "cond_child2", "text": "Q8: 观望的原因是", "type": QuestionType.CONDITIONAL,
     "parent_key": "cond_parent", "trigger_options": ["观望"]},
    {"key": "text2", "text": "Q9: 目前的痛点", "type": QuestionType.TEXT_INPUT, "options": None},
    {"key": "number2", "text": "Q10: 期望年收入范围", "type": QuestionType.NUMBER_INPUT, "options": None},
]


ndef build_option_map(opts):
    if not opts:
        return {}
    return {o["text"]: o.get("score", 0) for o in opts}


def calc_score_for_answer(q_def, ans_value):
    if q_def["type"] == QuestionType.SINGLE_CHOICE:
        opt_map = build_option_map(q_def.get("options"))
        return opt_map.get(ans_value, 0)
    if q_def["type"] == QuestionType.MULTI_CHOICE:
        opt_map = build_option_map(q_def.get("options"))
        if isinstance(ans_value, list):
            return sum(opt_map.get(v, 0) for v in ans_value)
    return 0


def get_active_org_ids(session):
    orgs = session.query(Organization).filter(Organization.is_active == True).all()
    if not orgs:
        return [None]
    return [org.id for org in orgs]


def main():
    session = SessionLocal()
    try:
        existing = session.query(Survey).filter(Survey.title == SURVEY_TITLE).first()
        if existing:
            session.query(SurveyAnswer).filter(SurveyAnswer.survey_id == existing.id).delete()
            session.query(SurveyQuestion).filter(SurveyQuestion.survey_id == existing.id).delete()
            session.delete(existing)
            session.commit()

        survey = Survey(
            title=SURVEY_TITLE,
            description="包含所有题型的测试问卷",
            created_by_user_id=CREATED_BY_USER_ID
        )
        session.add(survey)
        session.commit()
        session.refresh(survey)

        question_map = {}
        for order, qd in enumerate(QUESTION_DEFS, start=1):
            q = Question(
                text=qd["text"],
                type=qd["type"],
                options=json.dumps(qd.get("options"), ensure_ascii=False) if qd.get("options") else None,
                category_id=None,
                is_required=False,
                order=order,
                owner_id=CREATED_BY_USER_ID
            )
            session.add(q)
            session.commit()
            session.refresh(q)
            question_map[qd["key"]] = q
            session.add(SurveyQuestion(survey_id=survey.id, question_id=q.id, order=order))
            session.commit()
            parent_key = qd.get("parent_key")
            if parent_key:
                parent = question_map.get(parent_key)
                if parent:
                    q.parent_question_id = parent.id
                    q.trigger_options = json.dumps(qd.get("trigger_options", []), ensure_ascii=False)
                    session.add(q)
                    session.commit()

        org_ids = get_active_org_ids(session)
        for org_id in org_ids:
            for _ in range(ANSWER_COUNT_PER_ORG):
                answers_dict = {}
                total_score = 0
                for key, q in question_map.items():
                    q_def = next(item for item in QUESTION_DEFS if item["key"] == key)
                    qid = str(q.id)
                    qtype = q_def["type"]
                    if qtype == QuestionType.SINGLE_CHOICE:
                        opt = random.choice(q_def["options"])
                        answers_dict[qid] = opt["text"]
                        total_score += calc_score_for_answer(q_def, opt["text"])
                    elif qtype == QuestionType.MULTI_CHOICE:
                        opts = random.sample(q_def["options"], k=1)
                        values = [o["text"] for o in opts]
                        answers_dict[qid] = values
                        total_score += calc_score_for_answer(q_def, values)
                    elif qtype == QuestionType.NUMBER_INPUT:
                        value = random.randint(1, 12)
                        answers_dict[qid] = value
                    elif qtype == QuestionType.SORT_ORDER:
                        order_opts = [opt["text"] for opt in q_def["options"]]
                        random.shuffle(order_opts)
                        answers_dict[qid] = order_opts
                    elif qtype == QuestionType.CONDITIONAL:
                        parent_key = q_def.get("parent_key")
                        trigger = q_def.get("trigger_options", [])
                        parent_q = question_map.get(parent_key)
                        parent_answer = answers_dict.get(str(parent_q.id)) if parent_q else None
                        if parent_answer and parent_answer in trigger:
                            answers_dict[qid] = f"信息 {random.randint(1, 20)}"
                    else:
                        answers_dict[qid] = f"开放回答 {random.randint(1, 50)}"
                sa = SurveyAnswer(
                    survey_id=survey.id,
                    answers=json.dumps(answers_dict, ensure_ascii=False),
                    department=f"部门{random.randint(1,5)}",
                    position=f"岗位{random.randint(1,5)}",
                    organization_id=org_id,
                    organization_name=f"ORG-{org_id}" if org_id else None,
                    total_score=int(total_score)
                )
                session.add(sa)
        session.commit()
        print(f"Seed ready: survey_id={survey.id}, questions={len(question_map)}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
