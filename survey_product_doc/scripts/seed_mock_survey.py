import json
import random
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import text

from backend.app import crud
from backend.app.database import SessionLocal
from backend.app.models.survey import Survey
from backend.app.models.question import Question, QuestionType
from backend.app.models.survey_question import SurveyQuestion
from backend.app.models.answer import SurveyAnswer
from backend.app.models.organization import Organization
from backend.app.models.department import Department
from backend.app.schemas.question import QuestionCreate, QuestionUpdate

SURVEY_TITLE = "测试问卷 - 全题型覆盖"
SURVEY_DESCRIPTION = "用于验证各类题型与组织维度数据的模拟问卷"
CREATED_BY_USER_ID = 2
ANSWER_COUNT = 96
POSITIONS = ["工程师", "人力资源", "运营专员", "产品经理", "销售代表", "财务"]

QUESTION_DEFS = [
    {
        "key": "single_feedback",
        "text": "Q1: 你对当前产品满意吗？",
        "type": QuestionType.SINGLE_CHOICE,
        "options": [
            {"text": "非常满意", "score": 10},
            {"text": "满意", "score": 8},
            {"text": "一般", "score": 5},
            {"text": "不满意", "score": 2}
        ]
    },
    {
        "key": "multi_expectation",
        "text": "Q2: 你最看重哪些福利或资源？",
        "type": QuestionType.MULTI_CHOICE,
        "options": [
            {"text": "薪资", "score": 4},
            {"text": "培训", "score": 3},
            {"text": "弹性工作", "score": 2},
            {"text": "团队建设", "score": 1},
            {"text": "AI工具支持", "score": 2}
        ]
    },
    {
        "key": "text_suggestion",
        "text": "Q3: 你希望公司在哪些方面改进？",
        "type": QuestionType.TEXT_INPUT,
        "options": None
    },
    {
        "key": "number_overtime",
        "text": "Q4: 平均每周能投入多少小时加班？",
        "type": QuestionType.NUMBER_INPUT,
        "options": None,
        "min_value": 0,
        "max_value": 20
    },
    {
        "key": "sort_priority",
        "text": "Q5: 请对以下事项排序",
        "type": QuestionType.SORT_ORDER,
        "options": [
            {"text": "用户体验优化"},
            {"text": "内部流程改造"},
            {"text": "能力提升"},
            {"text": "新技术预研"}
        ]
    },
    {
        "key": "project_interest",
        "text": "Q6: 是否愿意参与跨部门专项项目？",
        "type": QuestionType.SINGLE_CHOICE,
        "options": [
            {"text": "愿意"},
            {"text": "观望"},
            {"text": "不参与"}
        ]
    },
    {
        "key": "project_area",
        "text": "Q7: 愿意参与时希望负责的方向是？",
        "type": QuestionType.CONDITIONAL,
        "parent_key": "project_interest",
        "trigger_options": ["愿意"]
    },
    {
        "key": "project_reason",
        "text": "Q8: 观望的原因是什么？",
        "type": QuestionType.CONDITIONAL,
        "parent_key": "project_interest",
        "trigger_options": ["观望"]
    },
    {
        "key": "project_refuse",
        "text": "Q9: 不参与的顾虑是？",
        "type": QuestionType.CONDITIONAL,
        "parent_key": "project_interest",
        "trigger_options": ["不参与"]
    },
    {
        "key": "number_salary",
        "text": "Q10: 期望的年薪区间（万元）",
        "type": QuestionType.NUMBER_INPUT,
        "options": None,
        "min_value": 15,
        "max_value": 40
    },
    {
        "key": "ai_usage",
        "text": "Q11: 你常用哪些AI工具？",
        "type": QuestionType.MULTI_CHOICE,
        "options": [
            {"text": "ChatGPT", "score": 2},
            {"text": "Copilot", "score": 2},
            {"text": "文心一言", "score": 1},
            {"text": "其他", "score": 1}
        ]
    },
    {
        "key": "ai_tool_detail",
        "text": "Q12: 关于AI工具使用的具体经验",
        "type": QuestionType.CONDITIONAL,
        "parent_key": "ai_usage",
        "trigger_options": ["ChatGPT", "Copilot", "文心一言", "其他"]
    }
]


def build_option_score_map(options: Optional[List[Dict[str, int]]]) -> Dict[str, int]:
    if not options:
        return {}
    return {opt["text"]: opt.get("score", 0) for opt in options}


def calc_score(q_def: Dict, answer_value) -> int:
    if q_def["type"] == QuestionType.SINGLE_CHOICE:
        return build_option_score_map(q_def.get("options")).get(answer_value, 0)
    if q_def["type"] == QuestionType.MULTI_CHOICE and isinstance(answer_value, list):
        score_map = build_option_score_map(q_def.get("options"))
        return sum(score_map.get(item, 0) for item in answer_value)
    return 0


def load_active_organizations(session):
    return session.query(Organization).filter(Organization.is_active == True).all()


def load_departments_for_org(session, org_id: int) -> List[str]:
    departments = session.query(Department).filter(
        Department.organization_id == org_id,
        Department.is_active == True
    ).all()
    if departments:
        return [dept.name for dept in departments]
    return [f"部门{idx}" for idx in range(1, 4)]


def log_question_schema(session):
    print("Question table structure:")
    columns = session.execute(text("SHOW FULL COLUMNS FROM questions")).all()
    for column in columns:
        print(f" - {column.Field}: type={column.Type}, null={column.Null}, key={column.Key}")

    types = session.execute(text("SELECT DISTINCT `type` FROM questions")).all()
    print("Current TYPE values:", [row[0] for row in types])


def clear_existing_data(session):
    existing_survey = session.query(Survey).filter(Survey.title == SURVEY_TITLE).first()
    if existing_survey:
        session.query(SurveyAnswer).filter(SurveyAnswer.survey_id == existing_survey.id).delete()
        session.query(SurveyQuestion).filter(SurveyQuestion.survey_id == existing_survey.id).delete()
        session.delete(existing_survey)
        session.commit()

    question_texts = [qd["text"] for qd in QUESTION_DEFS]
    session.query(Question).filter(
        Question.owner_id == CREATED_BY_USER_ID,
        Question.text.in_(question_texts)
    ).delete(synchronize_session=False)
    session.commit()


def create_questions(session) -> Dict[str, Question]:
    question_map: Dict[str, Question] = {}
    for order, q_def in enumerate(QUESTION_DEFS, start=1):
        question_payload = {
            "text": q_def["text"],
            "type": q_def["type"],
            "order": order,
            "is_required": False,
        }
        if q_def.get("options") is not None:
            question_payload["options"] = q_def["options"]
        if q_def.get("min_score") is not None:
            question_payload["min_score"] = q_def["min_score"]
        if q_def.get("max_score") is not None:
            question_payload["max_score"] = q_def["max_score"]
        if q_def.get("min_value") is not None:
            question_payload["min_score"] = q_def["min_value"]
        if q_def.get("max_value") is not None:
            question_payload["max_score"] = q_def["max_value"]

        question_create = QuestionCreate(**question_payload)
        question = crud.create_global_question(session, question_create, CREATED_BY_USER_ID)
        question_map[q_def["key"]] = question

        parent_key = q_def.get("parent_key")
        if parent_key:
            parent_question = question_map.get(parent_key)
            if parent_question:
                trigger_options = q_def.get("trigger_options", [])
                normalized_triggers = []
                for trigger in trigger_options:
                    if isinstance(trigger, dict) and "option_text" in trigger:
                        normalized_triggers.append(trigger)
                    else:
                        normalized_triggers.append({"option_text": trigger})

                update_data = QuestionUpdate(
                    parent_question_id=parent_question.id,
                    trigger_options=normalized_triggers
                )
                question = crud.update_question(session, question.id, update_data)
                question_map[q_def["key"]] = question

    return question_map


def link_questions_to_survey(session, survey: Survey, question_map: Dict[str, Question]):
    for order, question in enumerate(question_map.values(), start=1):
        session.add(SurveyQuestion(survey_id=survey.id, question_id=question.id, order=order))
    session.commit()


def generate_answers(
    session,
    survey: Survey,
    question_map: Dict[str, Question],
    organizations: List[Organization]
) -> int:
    total_answers = 0
    per_org = max(1, ANSWER_COUNT // max(1, len(organizations)))
    for org in organizations:
        dept_choices = load_departments_for_org(session, org.id)
        for _ in range(per_org):
            answers_payload = {}
            answer_context: Dict[str, object] = {}
            total_score = 0

            for q_def in QUESTION_DEFS:
                question = question_map.get(q_def["key"])
                if not question:
                    continue
                qid = str(question.id)

                parent_key = q_def.get("parent_key")
                if parent_key:
                    parent_value = answer_context.get(parent_key)
                    triggers = q_def.get("trigger_options", [])
                    if not parent_value:
                        continue
                    parent_values = parent_value if isinstance(parent_value, list) else [parent_value]
                    if not any(value in triggers for value in parent_values):
                        continue

                answer_value = None
                qtype = q_def["type"]
                if qtype == QuestionType.SINGLE_CHOICE:
                    option = random.choice(q_def["options"])
                    answer_value = option["text"]
                    total_score += calc_score(q_def, answer_value)
                elif qtype == QuestionType.MULTI_CHOICE:
                    option_count = random.randint(1, min(3, len(q_def["options"])))
                    selected = random.sample(q_def["options"], k=option_count)
                    answer_value = [item["text"] for item in selected]
                    total_score += calc_score(q_def, answer_value)
                elif qtype == QuestionType.NUMBER_INPUT:
                    min_val = q_def.get("min_value", 0)
                    max_val = q_def.get("max_value", min_val + 20)
                    answer_value = random.randint(min_val, max_val)
                elif qtype == QuestionType.SORT_ORDER:
                    sequence = [item["text"] for item in q_def["options"]]
                    random.shuffle(sequence)
                    answer_value = sequence
                else:
                    answer_value = f"自动生成内容 {random.randint(1, 100)}"

                answers_payload[qid] = answer_value
                answer_context[q_def["key"]] = answer_value

            survey_answer = SurveyAnswer(
                survey_id=survey.id,
                answers=json.dumps(answers_payload, ensure_ascii=False),
                department=random.choice(dept_choices),
                position=random.choice(POSITIONS),
                organization_id=org.id,
                organization_name=org.name,
                total_score=int(total_score),
                submitted_at=datetime.utcnow()
            )
            session.add(survey_answer)
            total_answers += 1
        session.commit()
    return total_answers


def main():
    session = SessionLocal()
    try:
        log_question_schema(session)
        organizations = load_active_organizations(session)
        if not organizations:
            print("未找到可用组织，请先创建组织后再运行脚本。")
            return

        clear_existing_data(session)

        survey = Survey(
            title=SURVEY_TITLE,
            description=SURVEY_DESCRIPTION,
            created_by_user_id=CREATED_BY_USER_ID
        )
        session.add(survey)
        session.commit()
        session.refresh(survey)

        question_map = create_questions(session)
        link_questions_to_survey(session, survey, question_map)

        answers_created = generate_answers(session, survey, question_map, organizations)

        print(
            f"脚本完成：survey_id={survey.id}，问题数量={len(question_map)}，"
            f"组织数量={len(organizations)}，答案数量={answers_created}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
