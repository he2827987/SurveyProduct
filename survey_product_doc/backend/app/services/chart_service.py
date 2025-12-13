from sqlalchemy.orm import Session
from backend.app.models.answer import SurveyAnswer
from backend.app.models.question import Question, QuestionType
import json
from typing import List, Dict, Any, Optional

def _resolve_group_value(ans: SurveyAnswer, dimension: str) -> str:
    if dimension == "department":
        return ans.department or "未知部门"
    if dimension == "position":
        return ans.position or "未知职位"
    if dimension == "organization":
        if ans.organization_name:
            return ans.organization_name
        if ans.organization_id is not None:
            return f"组织#{ans.organization_id}"
        return "未知组织"
    return "未指定"

def get_question_option_stats(
    db: Session,
    survey_id: int,
    dimension: str = "department",
    organization_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    统计调研中每个问题的选项被选择次数，并按指定维度分布。
    维度：department / position / organization
    包括“未作答”统计；填空题仅区分“有答案/未作答”
    """
    from backend.app.services.survey_service import get_survey_questions
    
    if dimension not in ["department", "position", "organization"]:
        return []
    
    # 1. 获取该问卷的所有问题
    questions = get_survey_questions(db, survey_id)
    if not questions:
        return []
        
    # 2. 获取该问卷的所有回答
    answers_query = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id)
    if organization_ids:
        answers_query = answers_query.filter(SurveyAnswer.organization_id.in_(organization_ids))
    answers = answers_query.all()
    
    stats_map: Dict[str, Dict[str, Any]] = {} # question_id -> option_text -> group -> count
    
    # 初始化统计结构
    for question in questions:
        q_id = str(question['id'])
        q_type = question['type']
        stats_map[q_id] = {
            "text": question['text'],
            "type": q_type,
            "options_stats": {}
        }
        
        # 选择题：初始化所有选项；非选择题：仅保留“有答案/未作答”
        if question.get('options') and q_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
            for opt in question['options']:
                opt_text = opt['text'] if isinstance(opt, dict) else opt
                stats_map[q_id]["options_stats"][opt_text] = {}
        else:
            stats_map[q_id]["options_stats"]["有答案"] = {}
        
        # 初始化 "未作答" 统计
        stats_map[q_id]["options_stats"]["(未作答)"] = {}

    for ans in answers:
        group_value = _resolve_group_value(ans, dimension)
        
        if not ans.answers:
            # 如果整个回答都为空，所有问题都算未作答
            for q_id in stats_map:
                stats_map[q_id]["options_stats"]["(未作答)"][group_value] = stats_map[q_id]["options_stats"]["(未作答)"].get(group_value, 0) + 1
            continue
            
        try:
            ans_data = json.loads(ans.answers)
        except (json.JSONDecodeError, TypeError):
            # 解析失败，视为未作答
            for q_id in stats_map:
                stats_map[q_id]["options_stats"]["(未作答)"][group_value] = stats_map[q_id]["options_stats"]["(未作答)"].get(group_value, 0) + 1
            continue
        
        # 遍历每个问题，判断是否回答
        for q_id, q_stats in stats_map.items():
            user_ans = ans_data.get(q_id)
            
            # 判断是否回答：None, 空字符串, 空列表 都算未回答
            has_answer = False
            if user_ans is not None:
                if isinstance(user_ans, str) and user_ans.strip():
                    has_answer = True
                elif isinstance(user_ans, (int, float)):
                    has_answer = True
                elif isinstance(user_ans, list) and len(user_ans) > 0:
                    has_answer = True
            
            if not has_answer:
                # 计入未作答
                q_stats["options_stats"]["(未作答)"][group_value] = q_stats["options_stats"]["(未作答)"].get(group_value, 0) + 1
            else:
                is_choice = q_stats["type"] in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]
                
                if is_choice:
                    selected_options = []
                    if isinstance(user_ans, str):
                        selected_options = [user_ans]
                    elif isinstance(user_ans, list):
                        selected_options = user_ans
                    elif isinstance(user_ans, (int, float)):
                        selected_options = [str(user_ans)]
                        
                    for opt_text in selected_options:
                        # 确保选项在统计map中（防止用户提交了不在选项列表中的值）
                        if opt_text not in q_stats["options_stats"]:
                            q_stats["options_stats"][opt_text] = {}
                        
                        q_stats["options_stats"][opt_text][group_value] = q_stats["options_stats"][opt_text].get(group_value, 0) + 1
                else:
                    # 非选择题：统一计入“有答案”
                    if "有答案" not in q_stats["options_stats"]:
                        q_stats["options_stats"]["有答案"] = {}
                    q_stats["options_stats"]["有答案"][group_value] = q_stats["options_stats"]["有答案"].get(group_value, 0) + 1

    # 3. 转换为前端友好的列表格式
    result = []
    for q_id, data in stats_map.items():
        options_data = []
        for opt_text, dept_dist in data["options_stats"].items():
            total = sum(dept_dist.values())
            options_data.append({
                "name": opt_text,
                "value": total,
                "breakdown": [{"name": k, "value": v} for k, v in dept_dist.items()]
            })
            
        result.append({
            "id": q_id,
            "title": data["text"],
            "type": data["type"],
            "data": options_data
        })
        
    return result
