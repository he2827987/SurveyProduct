# backend/app/services/survey_service.py

from sqlalchemy.orm import Session
from backend.app.models.survey import Survey as SurveyModel
from backend.app.schemas.survey import SurveyCreate, SurveyUpdate
from backend.app.models.user import User as UserModel # 导入 User 模型，用于类型提示

def create_survey(db: Session, survey: SurveyCreate, user_id: int):
    """
    创建一份新的问卷。
    如果提供了question_ids，则创建调研与题目的关联关系。
    """
    from backend.app.models.survey_question import SurveyQuestion

    db_survey = SurveyModel(
        title=survey.title,  # 使用survey.title，因为schema中定义的是title字段
        description=survey.description,
        created_by_user_id=user_id
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)

    # 如果提供了question_ids，则创建调研与题目的关联关系
    if survey.question_ids:
        for order, question_id in enumerate(survey.question_ids, 1):
            survey_question = SurveyQuestion(
                survey_id=db_survey.id,
                question_id=question_id,
                order=order
            )
            db.add(survey_question)
        db.commit()

    return db_survey

def get_survey(db: Session, survey_id: int):
    """
    根据 ID 获取问卷。
    """
    return db.query(SurveyModel).filter(SurveyModel.id == survey_id).first()

def get_surveys_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    获取某个用户创建的所有问卷。
    """
    return db.query(SurveyModel).filter(SurveyModel.created_by_user_id == user_id).offset(skip).limit(limit).all()

def get_global_surveys(db: Session, skip: int = 0, limit: int = 100, search: str = None, status_filter: str = None, sort_by: str = None):
    """
    获取全局调研库中的所有调研。
    支持搜索、状态筛选和排序。
    """
    query = db.query(SurveyModel)
    
    # 添加搜索过滤
    if search:
        query = query.filter(SurveyModel.title.contains(search))
    
    # 添加状态过滤
    if status_filter:
        query = query.filter(SurveyModel.status == status_filter)
    
    # 添加排序
    if sort_by:
        if sort_by == "created_desc":
            query = query.order_by(SurveyModel.created_at.desc())
        elif sort_by == "created_asc":
            query = query.order_by(SurveyModel.created_at.asc())
        elif sort_by == "title_asc":
            query = query.order_by(SurveyModel.title.asc())
        elif sort_by == "title_desc":
            query = query.order_by(SurveyModel.title.desc())
    else:
        # 默认按创建时间降序
        query = query.order_by(SurveyModel.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def update_survey(db: Session, survey_id: int, survey_update: SurveyUpdate):
    """
    更新问卷信息。
    如果提供了question_ids，则更新调研与题目的关联关系。
    """
    from backend.app.models.survey_question import SurveyQuestion

    db_survey = db.query(SurveyModel).filter(SurveyModel.id == survey_id).first()
    if db_survey:
        update_data = survey_update.model_dump(exclude_unset=True) # Pydantic v2: model_dump

        # 特殊处理question_ids：删除现有关联，创建新的关联
        if 'question_ids' in update_data:
            question_ids = update_data.pop('question_ids')  # 从更新数据中移除，避免直接设置到SurveyModel

            # 删除现有的survey-question关联
            db.query(SurveyQuestion).filter(SurveyQuestion.survey_id == survey_id).delete()

            # 创建新的关联
            if question_ids:
                for order, question_id in enumerate(question_ids, 1):
                    survey_question = SurveyQuestion(
                        survey_id=survey_id,
                        question_id=question_id,
                        order=order
                    )
                    db.add(survey_question)

        # 更新其他字段
        for key, value in update_data.items():
            setattr(db_survey, key, value)

        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
    return db_survey

def delete_survey(db: Session, survey_id: int):
    """
    删除问卷。
    """
    db_survey = db.query(SurveyModel).filter(SurveyModel.id == survey_id).first()
    if db_survey:
        db.delete(db_survey)
        db.commit()
    return db_survey

# 辅助函数：检查用户是否是问卷的创建者
def is_survey_creator(db: Session, survey_id: int, user_id: int):
    """
    检查给定用户是否是指定问卷的创建者。
    """
    survey = db.query(SurveyModel).filter(SurveyModel.id == survey_id).first()
    # 更简洁的写法
    return survey is not None and survey.created_by_user_id == user_id

def get_survey_questions(db: Session, survey_id: int):
    """
    获取调研的题目列表
    """
    from backend.app.models.survey_question import SurveyQuestion
    from backend.app.models.question import Question
    
    # 首先检查调研是否存在
    survey = db.query(SurveyModel).filter(SurveyModel.id == survey_id).first()
    if not survey:
        return None
    
    # 通过SurveyQuestion关联表获取题目
    survey_questions = db.query(SurveyQuestion).filter(
        SurveyQuestion.survey_id == survey_id
    ).order_by(SurveyQuestion.order).all()
    
    questions = []
    for sq in survey_questions:
        question = db.query(Question).filter(Question.id == sq.question_id).first()
        if question:
            # 转换选项格式
            options = []
            if question.options:
                try:
                    import json
                    options = json.loads(question.options) if isinstance(question.options, str) else question.options
                except:
                    options = []
            
            questions.append({
                "id": question.id,
                "text": question.text,
                "type": question.type,
                "options": options,
                "is_required": question.is_required,
                "order": sq.order,
                "min_score": question.min_score,
                "max_score": question.max_score
            })
    
    return questions
