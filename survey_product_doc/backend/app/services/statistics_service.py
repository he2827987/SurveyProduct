
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.answer import SurveyAnswer
from backend.app.models.question import QuestionType
from typing import List, Dict, Any, Optional
import json

def get_survey_stats_by_dimension(db: Session, survey_id: int, dimension: str) -> List[Dict[str, Any]]:
    """
    按维度统计调研数据（总分、平均分）
    dimension: 'department' | 'position'
    """
    if dimension not in ['department', 'position']:
        return []

    # 动态选择分组字段
    group_field = getattr(SurveyAnswer, dimension)
    
    stats = db.query(
        group_field.label('group_key'),
        func.count(SurveyAnswer.id).label('count'),
        func.sum(SurveyAnswer.total_score).label('total_score_sum'),
        func.avg(SurveyAnswer.total_score).label('average_score')
    ).filter(
        SurveyAnswer.survey_id == survey_id,
        group_field.isnot(None) # 排除未填写部门/职位的
    ).group_by(
        group_field
    ).all()
    
    result = []
    for row in stats:
        result.append({
            "dimension": dimension,
            "key": row.group_key,
            "count": row.count,
            "total_score_sum": float(row.total_score_sum) if row.total_score_sum else 0,
            "average_score": float(row.average_score) if row.average_score else 0
        })
        
    return result


def get_per_question_scores(
    db: Session,
    survey_id: int,
    department: Optional[str] = None,
    position: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    统计指定问卷内每个问题的总分和平均分，可按部门、职位过滤回答者。
    返回：
    [
      {
        "question_id": 1,
        "question_text": "...",
        "response_count": 10,
        "total_score": 85.0,
        "avg_score": 8.5
      },
      ...
    ]
    """
    from backend.app.services.grading_service import calculate_answer_score
    from backend.app.services.survey_service import get_survey_questions
    from backend.app.models.question import Question as QuestionModel

    questions_in_survey = get_survey_questions(db, survey_id)
    question_map: Dict[str, Dict[str, Any]] = {}
    for q in questions_in_survey:
        qid_str = str(q["id"])
        question_map[qid_str] = {
            "question_id": q["id"],
            "question_text": q["text"],
            "total_score": 0.0,
            "response_count": 0
        }

    if not question_map:
        return []

    query = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id)
    if department is not None:
        query = query.filter(SurveyAnswer.department == department)
    if position is not None:
        query = query.filter(SurveyAnswer.position == position)

    answers = query.all()

    q_models = db.query(QuestionModel).filter(QuestionModel.id.in_([q["id"] for q in questions_in_survey])).all()
    q_model_map: Dict[str, QuestionModel] = {str(q.id): q for q in q_models}

    for ans in answers:
        if not ans.answers:
            continue
        try:
            ans_data = json.loads(ans.answers)
        except (json.JSONDecodeError, TypeError):
            continue

        for qid_str, user_ans in ans_data.items():
            if qid_str not in question_map:
                continue
            q_model = q_model_map.get(qid_str)
            if not q_model:
                continue
            score = calculate_answer_score(q_model, user_ans)
            question_map[qid_str]["total_score"] += score
            question_map[qid_str]["response_count"] += 1

    result = []
    for qid_str, info in question_map.items():
        count = info["response_count"]
        total = info["total_score"]
        avg = round(total / count, 2) if count > 0 else 0.0
        result.append({
            "question_id": info["question_id"],
            "question_text": info["question_text"],
            "response_count": count,
            "total_score": round(total, 2),
            "avg_score": avg
        })

    return result



def get_line_scores_by_dimension(db: Session, survey_id: int, dimension: str = "department", question_ids: Optional[List[int]] = None, include_survey_total: bool = False) -> Dict[str, Any]:
    """
    计算折线图数据：X轴为人群（部门/职位），Y轴为平均分。
    - question_ids 为空且 include_survey_total=True: 按问卷总分聚合
    - question_ids 不为空: 按指定题目聚合平均分
    可同时返回多条 series（问卷总分 + 多题）。
    """
    if dimension not in ["department", "position"]:
        raise ValueError("dimension must be 'department' or 'position'")

    from backend.app.models.answer import SurveyAnswer as SurveyAnswerModel
    from backend.app.models.question import Question as QuestionModel
    from backend.app.services.grading_service import calculate_answer_score
    from backend.app.services.survey_service import get_survey_questions
    import json

    # 拉取答卷
    answers_query = db.query(SurveyAnswerModel).filter(SurveyAnswerModel.survey_id == survey_id)
    answers = answers_query.all()

    # 收集人群列表
    categories_set = set()
    for ans in answers:
        key = ans.department if dimension == "department" else ans.position
        key = key or "未知%s" % ("部门" if dimension == "department" else "职位")
        categories_set.add(key)
    categories = sorted(categories_set)

    series = []

    # 1) 问卷总分
    if include_survey_total:
        totals_map = {cat: {"sum": 0.0, "count": 0} for cat in categories}
        for ans in answers:
            key = ans.department if dimension == "department" else ans.position
            key = key or "未知%s" % ("部门" if dimension == "department" else "职位")
            if ans.total_score is not None:
                totals_map[key]["sum"] += ans.total_score
                totals_map[key]["count"] += 1
        data = []
        for cat in categories:
            c = totals_map[cat]
            avg = c["sum"] / c["count"] if c["count"] > 0 else 0.0
            data.append(round(avg, 2))
        series.append({"name": "问卷总分", "data": data})

    # 2) 按题目（仅统计有分值的单/多选题）
    if question_ids:
        q_objs = db.query(QuestionModel).filter(QuestionModel.id.in_(question_ids)).all()

        def is_scored_choice(q: QuestionModel) -> bool:
            if q.type not in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
                return False
            try:
                opts = json.loads(q.options) if isinstance(q.options, str) else (q.options or [])
            except Exception:
                return False
            return any(isinstance(o, dict) and o.get("score") is not None for o in opts)

        q_map = {q.id: q for q in q_objs if is_scored_choice(q)}
        if not q_map:
            return {"categories": categories, "series": series}

        # 准备聚合结构：qid -> cat -> {sum, count}
        agg: Dict[int, Dict[str, Dict[str, float]]] = {
            qid: {cat: {"sum": 0.0, "count": 0} for cat in categories}
            for qid in q_map.keys()
        }

        for ans in answers:
            key = ans.department if dimension == "department" else ans.position
            key = key or "未知%s" % ("部门" if dimension == "department" else "职位")
            try:
                ans_data = json.loads(ans.answers)
            except Exception:
                continue

            for qid, q_obj in q_map.items():
                if str(qid) not in ans_data:
                    continue
                val = ans_data.get(str(qid))
                score = calculate_answer_score(q_obj, val)
                agg[qid][key]["sum"] += score
                # 只有有回答才计数
                if val is not None and (str(val).strip() != '' if not isinstance(val, list) else len(val) > 0):
                    agg[qid][key]["count"] += 1

        for qid, cat_map in agg.items():
            data = []
            for cat in categories:
                c = cat_map[cat]
                avg = c["sum"] / c["count"] if c["count"] > 0 else 0.0
                data.append(round(avg, 2))
            q_obj = q_map[qid]
            series.append({"name": f"Q{qid} {q_obj.text}", "data": data})
    return {"categories": categories, "series": series}



from backend.app.services.survey_service import get_survey_questions

def get_pie_option_distribution(
    db: Session,
    survey_id: int,
    question_id: int,
    option_text: str,
    dimension: str = "department",
    include_unanswered: bool = True
) -> Dict[str, Any]:
    """
    统计指定题目的某个选项在不同人群下的选择占比，生成饼图数据。
    - dimension: 'department' | 'position'
    - option_text: 选项文本；如果选择未作答，则传"(未作答)"
    - include_unanswered: 是否包含未作答作为一个扇区
    """
    if dimension not in ["department", "position"]:
        raise ValueError("dimension must be 'department' or 'position'")

    from backend.app.models.answer import SurveyAnswer as SurveyAnswerModel
    from backend.app.models.question import Question as QuestionModel

    question_obj = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not question_obj:
        return {"option": option_text, "dimension": dimension, "data": []}

    answers = db.query(SurveyAnswerModel).filter(SurveyAnswerModel.survey_id == survey_id).all()

    result_map: Dict[str, int] = {}
    for ans in answers:
        key = ans.department if dimension == "department" else ans.position
        key = key or "未知%s" % ("部门" if dimension == "department" else "职位")

        try:
            ans_data = json.loads(ans.answers) if ans.answers else {}
        except Exception:
            ans_data = {}

        user_val = ans_data.get(str(question_id))

        has_answer = False
        if user_val is not None:
            if isinstance(user_val, str) and user_val.strip():
                has_answer = True
            elif isinstance(user_val, list) and len(user_val) > 0:
                has_answer = True
            elif isinstance(user_val, (int, float)):
                has_answer = True

        if not has_answer:
            if include_unanswered:
                result_map["(未作答)"] = result_map.get("(未作答)", 0) + 1
            continue

        matched = False
        if isinstance(user_val, list):
            if option_text in user_val:
                matched = True
        else:
            if str(user_val) == option_text:
                matched = True

        if matched:
            result_map[key] = result_map.get(key, 0) + 1

    data = [{"name": k, "value": v} for k, v in result_map.items()]
    return {
        "option": option_text,
        "dimension": dimension,
        "data": data
    }
