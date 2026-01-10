
from sqlalchemy.orm import Session
from backend.app.models.question import Question, QuestionType
from backend.app.models.answer import SurveyAnswer
import json
from typing import List, Dict, Any

def calculate_answer_score(question: Question, answer_value: Any) -> float:
    """
    计算单个问题的得分
    """
    if not answer_value:
        return 0.0

    # 解析选项
    options = []
    if question.options:
        try:
            options = json.loads(question.options) if isinstance(question.options, str) else question.options
        except:
            options = []

    score = 0.0

    if question.type == QuestionType.SINGLE_CHOICE:
        # 单选题：找到匹配的选项，累加分数
        if isinstance(answer_value, str): # 假设单选答案是选项文本
             for opt in options:
                # 兼容旧格式和新格式
                opt_text = opt.get('text') if isinstance(opt, dict) else opt
                opt_score = opt.get('score', 0) if isinstance(opt, dict) else 0
                opt_correct = opt.get('is_correct', False) if isinstance(opt, dict) else False
                
                if opt_text == answer_value:
                    score += float(opt_score)
                    # 如果没有设置具体分值但设置了正确答案，默认给1分（或者根据业务规则调整）
                    if opt_score == 0 and opt_correct:
                        score += 1.0 
                    break

    elif question.type == QuestionType.MULTI_CHOICE:
        # 多选题：遍历所有选中项
        if isinstance(answer_value, list):
            for val in answer_value:
                for opt in options:
                    opt_text = opt.get('text') if isinstance(opt, dict) else opt
                    opt_score = opt.get('score', 0) if isinstance(opt, dict) else 0
                    opt_correct = opt.get('is_correct', False) if isinstance(opt, dict) else False

                    if opt_text == val:
                        score += float(opt_score)
                        if opt_score == 0 and opt_correct:
                            score += 1.0
                        break
    
    # 填空题和数字题暂时不支持自动评分，除非有标准答案匹配逻辑（此处略）
    
    return score

def calculate_survey_total_score(db: Session, survey_id: int, answers_data: Dict[str, Any]) -> float:
    """
    计算整份问卷的总分
    """
    from backend.app.services.survey_service import get_survey_questions
    
    # 获取问卷题目
    # 注意：这里直接复用 get_survey_questions 可能会返回 dict 列表而不是 ORM 对象
    # 我们直接查询 ORM 对象以便使用
    from backend.app.models.survey_question import SurveyQuestion
    
    survey_questions_relations = db.query(SurveyQuestion).filter(
        SurveyQuestion.survey_id == survey_id
    ).all()
    
    total_score = 0.0
    
    for sq in survey_questions_relations:
        question = db.query(Question).filter(Question.id == sq.question_id).first()
        if not question:
            continue
            
        # 答案中的 key 通常是 question_id (str)
        ans_val = answers_data.get(str(question.id))
        if ans_val:
            total_score += calculate_answer_score(question, ans_val)
            
    return total_score

