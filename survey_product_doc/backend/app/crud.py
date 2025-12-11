# backend/app/crud.py
"""
数据库CRUD操作模块
提供用户、调研、问题、答案、组织等实体的数据库操作函数
"""

# ===== 导入依赖 =====
from sqlalchemy.orm import Session
from typing import List, Optional, cast, Union
from backend.app import models
from backend.app import schemas
from backend.app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyResponse
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.schemas.question import QuestionCreate, QuestionUpdate
from backend.app.schemas.answer import SurveyAnswerCreate, SurveyAnswer
from backend.app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from backend.app.schemas.organization_member import OrganizationMemberCreate, OrganizationMemberUpdate, OrganizationMemberResponse
from backend.app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from passlib.context import CryptContext # type: ignore
import json

# ===== 密码处理配置 =====
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== 密码处理辅助函数 =====

def get_password_hash(password: str) -> str:
    """
    对密码进行哈希处理
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

# ===== User CRUD 操作 =====

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    根据 ID 获取单个用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Optional[models.User]: 用户对象，如果不存在则返回None
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    根据邮箱获取单个用户
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        
    Returns:
        Optional[models.User]: 用户对象，如果不存在则返回None
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    获取用户列表，支持分页
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.User]: 用户列表
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> models.User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user: 用户创建数据
        
    Returns:
        models.User: 创建的用户对象
    """
    # 对密码进行哈希处理
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[models.User]:
    """
    更新用户信息
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        user_update: 用户更新数据
        
    Returns:
        Optional[models.User]: 更新后的用户对象，如果用户不存在则返回None
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # 只更新Pydantic模型中设置的字段
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        bool: 删除成功返回True，用户不存在返回False
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# ===== Survey CRUD 操作 =====

def get_survey(db: Session, survey_id: int) -> Optional[models.Survey]:
    """
    根据 ID 获取单个问卷
    
    Args:
        db: 数据库会话
        survey_id: 问卷ID
        
    Returns:
        Optional[models.Survey]: 问卷对象，如果不存在则返回None
    """
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()

def get_surveys(db: Session, skip: int = 0, limit: int = 100) -> List[models.Survey]:
    """
    获取问卷列表，支持分页
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.Survey]: 问卷列表
    """
    return db.query(models.Survey).offset(skip).limit(limit).all()

def create_survey(db: Session, survey: SurveyCreate, user_id: int) -> models.Survey:
    """
    创建新问卷，并关联到创建用户
    
    Args:
        db: 数据库会话
        survey: 问卷创建数据
        user_id: 创建用户的ID
        
    Returns:
        models.Survey: 创建的问卷对象
    """
    db_survey = models.Survey(
        text=survey.text,
        description=survey.description,
        created_by_user_id=user_id
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

def update_survey(db: Session, survey_id: int, survey_update: SurveyUpdate) -> Optional[models.Survey]:
    """
    更新问卷信息
    
    Args:
        db: 数据库会话
        survey_id: 问卷ID
        survey_update: 问卷更新数据
        
    Returns:
        Optional[models.Survey]: 更新后的问卷对象，如果问卷不存在则返回None
    """
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if db_survey:
        update_data = survey_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_survey, key, value)
        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
    return db_survey

def delete_survey(db: Session, survey_id: int) -> Optional[models.Survey]:
    """
    删除问卷
    
    Args:
        db: 数据库会话
        survey_id: 问卷ID
        
    Returns:
        Optional[models.Survey]: 被删除的问卷对象，如果问卷不存在则返回None
    """
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if db_survey:
        db.delete(db_survey)
        db.commit()
    return db_survey

# ===== Question CRUD 操作 =====

def get_question(db: Session, question_id: int) -> Optional[models.Question]:
    """
    根据 ID 获取单个问题
    
    Args:
        db: 数据库会话
        question_id: 问题ID
        
    Returns:
        Optional[models.Question]: 问题对象，如果不存在则返回None
    """
    # 从数据库查询问题对象
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    # 处理options字段：将JSON字符串转换为Python列表
    if db_question and db_question.options and isinstance(db_question.options, str):
        try:
            # 使用object.__setattr__直接设置属性，绕过ORM的property
            object.__setattr__(db_question, 'options', json.loads(db_question.options))
        except (json.JSONDecodeError, TypeError) as decode_error:
            # JSON解析失败时记录警告并设为空列表
            print(f"Warning: Could not decode options for question ID {db_question.id}. Options: {db_question.options}. Error: {decode_error}")    
            object.__setattr__(db_question, 'options', [])
    
    return db_question

def get_questions_by_survey(db: Session, survey_id: int, skip: int = 0, limit: int = 100) -> List[models.Question]:
    """
    获取指定问卷的所有问题，支持分页
    
    Args:
        db: 数据库会话
        survey_id: 问卷ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.Question]: 问题列表
    """
    from backend.app.models.survey_question import SurveyQuestion
    
    # 通过中间表获取题目
    survey_questions = db.query(SurveyQuestion).filter(
        SurveyQuestion.survey_id == survey_id
    ).order_by(SurveyQuestion.order).offset(skip).limit(limit).all()
    
    questions = []
    for sq in survey_questions:
        question = db.query(models.Question).filter(models.Question.id == sq.question_id).first()
        if question:
            questions.append(question)
    
    return questions

def create_survey_question(db: Session, question: QuestionCreate, survey_id: int) -> models.Question:
    """
    为指定问卷创建新问题（通过中间表关联）
    
    Args:
        db: 数据库会话
        question: 问题创建数据
        survey_id: 问卷ID
        
    Returns:
        models.Question: 创建的问题对象
    """
    from backend.app.models.survey_question import SurveyQuestion
    
    # 创建全局题目
    question_data = question.dict(exclude_unset=True, exclude={"options", "tags"})
    tags_data = question.tags
    
    # 确保设置owner_id
    if "owner_id" not in question_data:
        # 从调研中获取创建者ID
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if survey:
            question_data["owner_id"] = survey.created_by_user_id
    
    # 确保设置默认值
    if "usage_count" not in question_data:
        question_data["usage_count"] = 0
    if "order" not in question_data:
        question_data["order"] = 0
    
    print(f"Debug: 创建问题数据: {question_data}")  # 调试信息
    
    db_question = models.Question(
        **question_data,
        survey_id=None  # 全局题目，不直接关联到调研
    )
    
    # 处理 options，序列化为 JSON 字符串
    if question.options is not None:
        options_data = question.options
        # 如果是 Pydantic 对象列表，先转为 dict
        if isinstance(options_data, list):
            options_data = [
                opt.dict() if hasattr(opt, 'dict') else opt 
                for opt in options_data
            ]
        db_question.options = cast(str, json.dumps(options_data, ensure_ascii=False))

    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # 处理标签
    if tags_data:
        from backend.app.models.tag import Tag
        for tag_name in tags_data:
            # 查找或创建标签
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            # 添加关联
            db_question.tags.append(tag)
        db.commit()
    
    # 通过中间表关联到调研
    survey_question = SurveyQuestion(
        survey_id=survey_id,
        question_id=db_question.id,
        order=0  # 默认排序
    )
    db.add(survey_question)
    db.commit()
    
    return db_question

def update_question(db: Session, question_id: int, question_update: QuestionUpdate) -> Optional[models.Question]:
    """
    更新问题信息
    
    Args:
        db: 数据库会话
        question_id: 问题ID
        question_update: 问题更新数据
        
    Returns:
        Optional[models.Question]: 更新后的问题对象，如果问题不存在则返回None
    """
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        update_data = question_update.dict(exclude_unset=True)
        
        # 处理 tags
        if "tags" in update_data:
            tags_data = update_data["tags"]
            if tags_data is not None:
                # 清除旧标签关联
                db_question.tags = []
                
                from backend.app.models.tag import Tag
                for tag_name in tags_data:
                    # 查找或创建标签
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.commit()
                        db.refresh(tag)
                    
                    # 添加关联
                    db_question.tags.append(tag)
            
            del update_data["tags"]

        # 特殊处理options字段
        if "options" in update_data:
            if update_data["options"] is not None:
                options_data = update_data["options"]
                # 如果是 Pydantic 对象列表，先转为 dict
                if isinstance(options_data, list):
                    options_data = [
                        opt.dict() if hasattr(opt, 'dict') else opt 
                        for opt in options_data
                    ]
                db_question.options = cast(str, json.dumps(options_data, ensure_ascii=False))
            else:
                db_question.options = None # 如果更新为None，则清空
            del update_data["options"] # 从update_data中移除，避免重复处理

        for key, value in update_data.items():
            setattr(db_question, key, value)

        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        # 在返回前，强制将options转换为列表
        if db_question.options and isinstance(db_question.options, str):
            try:
                db_question.options = json.loads(db_question.options)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error decoding options for updated question ID {db_question.id}: {e}")
                db_question.options = []
    return db_question

def delete_question(db: Session, question_id: int) -> Optional[models.Question]:
    """
    删除问题
    
    Args:
        db: 数据库会话
        question_id: 问题ID
        
    Returns:
        Optional[models.Question]: 被删除的问题对象，如果问题不存在则返回None
    """
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
    return db_question

# ===== 全局题库 CRUD 操作 =====

def create_global_question(db: Session, question: schemas.QuestionCreate, owner_id: int) -> models.Question:
    """
    在全局题库中创建一个新问题
    
    Args:
        db: 数据库会话
        question: 问题创建数据
        owner_id: 问题创建者ID
        
    Returns:
        models.Question: 创建的问题对象
    """
    # 将Pydantic模型转换为字典，排除unset的字段
    question_data = question.dict()
    tags_data = question_data.pop('tags', []) if 'tags' in question_data else []

    question_data['owner_id'] = owner_id
    
    # 序列化options列表为JSON字符串
    if 'options' in question_data and question_data['options'] is not None:
        options_data = question_data['options']
        # 如果是 Pydantic 对象列表，先转为 dict (question.dict() 应该已经处理了，但为了保险起见)
        if isinstance(options_data, list):
            options_data = [
                opt if isinstance(opt, (dict, str)) else opt.dict()
                for opt in options_data
            ]
        question_data['options'] = json.dumps(options_data, ensure_ascii=False)
        
    db_question = models.Question(**question_data)
    # 如果QuestionCreate中没有survey_id，它将是None
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # 处理标签
    if tags_data:
        from backend.app.models.tag import Tag
        for tag_name in tags_data:
            # 查找或创建标签
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            # 添加关联
            db_question.tags.append(tag)
        db.commit()

    # 在返回前，强制将options转换为列表
    if db_question.options and isinstance(db_question.options, str):
        try:
            db_question.options = json.loads(db_question.options)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding options for newly created question ID {db_question.id}: {e}")
    return db_question

def get_global_questions(db: Session, skip: int = 0, limit: int = 100, type_filter: str = None, search_filter: str = None, sort_by: str = None, category_filter: int = None, tag_filter: List[str] = None) -> dict:
    """
    获取全局题库中的问题，支持分页和类型筛选
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        type_filter: 问题类型筛选
        
    Returns:
        dict: 包含问题列表和分页信息的字典
    """
    # 构建基础查询 - 现在所有题目都是全局题目
    base_query = db.query(models.Question)
    
    if type_filter:
        base_query = base_query.filter(models.Question.type == type_filter)
    
    # 添加搜索过滤
    if search_filter:
        base_query = base_query.filter(models.Question.text.contains(search_filter))
    
    # 添加分类过滤
    if category_filter:
        base_query = base_query.filter(models.Question.category_id == category_filter)
    
    # 添加标签过滤
    if tag_filter:
        from backend.app.models.tag import Tag
        base_query = base_query.join(models.Question.tags).filter(Tag.name.in_(tag_filter))
    
    # 添加排序
    if sort_by:
        if sort_by == "created_desc":
            base_query = base_query.order_by(models.Question.id.desc())
        elif sort_by == "created_asc":
            base_query = base_query.order_by(models.Question.id.asc())
        elif sort_by == "usage_desc":
            base_query = base_query.order_by(models.Question.usage_count.desc())
        elif sort_by == "usage_asc":
            base_query = base_query.order_by(models.Question.usage_count.asc())
    
    # 获取总数
    total = base_query.count()
    
    # 使用join查询来获取用户信息
    query = db.query(models.Question, models.User.username.label('owner_name'))
    # 现在所有题目都是全局题目
    query = query.outerjoin(models.User, models.Question.owner_id == models.User.id)
    
    if type_filter:
        query = query.filter(models.Question.type == type_filter)
    
    # 添加搜索过滤
    if search_filter:
        query = query.filter(models.Question.text.contains(search_filter))
    
    # 添加分类过滤
    if category_filter:
        query = query.filter(models.Question.category_id == category_filter)
    
    # 添加标签过滤
    if tag_filter:
        from backend.app.models.tag import Tag
        query = query.join(models.Question.tags).filter(Tag.name.in_(tag_filter))
    
    # 添加排序
    if sort_by:
        if sort_by == "created_desc":
            query = query.order_by(models.Question.id.desc())
        elif sort_by == "created_asc":
            query = query.order_by(models.Question.id.asc())
        elif sort_by == "usage_desc":
            query = query.order_by(models.Question.usage_count.desc())
        elif sort_by == "usage_asc":
            query = query.order_by(models.Question.usage_count.asc())
        
    # 获取结果
    results = query.offset(skip).limit(limit).all()
    
    # 处理结果，将用户信息添加到问题对象中
    questions = []
    for question, owner_name in results:
        # 处理options字段
        if question.options and isinstance(question.options, str):
            try:
                # 尝试将字符串解析为JSON列表
                object.__setattr__(question, 'options', json.loads(question.options))
            except json.JSONDecodeError as decode_error:
                # 如果解析失败，则设为空列表并记录日志
                print(f"Warning: Could not decode options for question ID {question.id}. Options: {question.options}. Error: {decode_error}")
                object.__setattr__(question, 'options', [])
        
        # 添加创建者用户名
        object.__setattr__(question, 'owner_name', owner_name)
        questions.append(question)
    
    # 计算分页信息
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        'items': questions,
        'total': total,
        'skip': skip,
        'limit': limit,
        'page': page,
        'pages': pages
    }

# ===== 组织题库 CRUD 操作 =====

def create_organization_question(db: Session, question: schemas.QuestionCreate, owner_id: int, organization_id: int) -> models.Question:
    """
    在组织题库中创建一个新问题
    
    Args:
        db: 数据库会话
        question: 问题创建数据
        owner_id: 问题创建者ID
        organization_id: 组织ID
        
    Returns:
        models.Question: 创建的问题对象
    """
    # 将Pydantic模型转换为字典，排除unset的字段
    question_data = question.dict()
    question_data['owner_id'] = owner_id
    question_data['organization_id'] = organization_id
    
    # 序列化options列表为JSON字符串
    if 'options' in question_data and question_data['options'] is not None:
        options_data = question_data['options']
        # 确保数据可序列化
        if isinstance(options_data, list):
            options_data = [
                opt if isinstance(opt, (dict, str)) else opt.dict()
                for opt in options_data
            ]
        question_data['options'] = json.dumps(options_data, ensure_ascii=False)
        
    db_question = models.Question(**question_data)
    # 如果QuestionCreate中没有survey_id，它将是None
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    # 在返回前，强制将options转换为列表
    if db_question.options and isinstance(db_question.options, str):
        try:
            db_question.options = json.loads(db_question.options)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding options for newly created question ID {db_question.id}: {e}")
    return db_question

def get_organization_questions(db: Session, org_id: int, skip: int = 0, limit: int = 100, type_filter: str = None, search_filter: str = None, sort_by: str = None) -> dict:
    """
    获取组织题库中的问题，支持分页和类型筛选
    
    Args:
        db: 数据库会话
        org_id: 组织ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        type_filter: 问题类型筛选
        
    Returns:
        dict: 包含问题列表和分页信息的字典
    """
    # 构建基础查询
    base_query = db.query(models.Question)
    base_query = base_query.filter(models.Question.organization_id == org_id)
    base_query = base_query.filter(models.Question.survey_id.is_(None))
    
    if type_filter:
        base_query = base_query.filter(models.Question.type == type_filter)
    
    # 添加搜索过滤
    if search_filter:
        base_query = base_query.filter(models.Question.text.contains(search_filter))
    
    # 添加排序
    if sort_by:
        if sort_by == "created_desc":
            base_query = base_query.order_by(models.Question.id.desc())
        elif sort_by == "created_asc":
            base_query = base_query.order_by(models.Question.id.asc())
        elif sort_by == "usage_desc":
            base_query = base_query.order_by(models.Question.usage_count.desc())
        elif sort_by == "usage_asc":
            base_query = base_query.order_by(models.Question.usage_count.asc())
    
    # 获取总数
    total = base_query.count()
    
    # 使用join查询来获取用户信息
    query = db.query(models.Question, models.User.username.label('owner_name'))
    # 筛选指定组织的问题，且survey_id为NULL
    query = query.outerjoin(models.User, models.Question.owner_id == models.User.id)
    query = query.filter(models.Question.organization_id == org_id)
    query = query.filter(models.Question.survey_id.is_(None))
    
    if type_filter:
        query = query.filter(models.Question.type == type_filter)
    
    # 添加搜索过滤
    if search_filter:
        query = query.filter(models.Question.text.contains(search_filter))
    
    # 添加排序
    if sort_by:
        if sort_by == "created_desc":
            query = query.order_by(models.Question.id.desc())
        elif sort_by == "created_asc":
            query = query.order_by(models.Question.id.asc())
        elif sort_by == "usage_desc":
            query = query.order_by(models.Question.usage_count.desc())
        elif sort_by == "usage_asc":
            query = query.order_by(models.Question.usage_count.asc())
        
    # 获取结果
    results = query.offset(skip).limit(limit).all()
    
    # 处理结果，将用户信息添加到问题对象中
    questions = []
    for question, owner_name in results:
        # 处理options字段
        if question.options and isinstance(question.options, str):
            try:
                # 尝试将字符串解析为JSON列表
                object.__setattr__(question, 'options', json.loads(question.options))
            except json.JSONDecodeError as decode_error:
                # 如果解析失败，则设为空列表并记录日志
                print(f"Warning: Could not decode options for question ID {question.id}. Options: {question.options}. Error: {decode_error}")
                object.__setattr__(question, 'options', [])
        
        # 添加创建者用户名
        object.__setattr__(question, 'owner_name', owner_name)
        questions.append(question)
    
    # 计算分页信息
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        'items': questions,
        'total': total,
        'skip': skip,
        'limit': limit,
        'page': page,
        'pages': pages
    }

# ===== Survey Answer CRUD 操作 =====

from backend.app.services.grading_service import calculate_survey_total_score

def create_survey_answer(
    db: Session,
    answer: SurveyAnswerCreate,
    survey_id: int,
    user_id: Optional[int] = None,
    participant_id: Optional[int] = None
) -> models.SurveyAnswer:
    """
    创建调研答案
    """
    # 计算总分
    total_score = calculate_survey_total_score(db, survey_id, answer.answers)

    # 提取部门和职位（如果 answer 中有这些字段）
    # 注意：answer.answers 仅包含题目答案，department/position 在 answer 对象本身
    # 如果 SurveyAnswerCreate 没有定义这些字段，需要修改 schema 或者从 extra 字段获取
    department = getattr(answer, 'department', None)
    position = getattr(answer, 'position', None)

    # 将answers字典转换为JSON字符串存储
    db_answer = models.SurveyAnswer(
        survey_id=survey_id,
        user_id=user_id,
        participant_id=participant_id,
        answers=json.dumps(answer.answers),
        total_score=total_score,
        department=department,
        position=position
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def get_survey_answers_by_survey_id(
    db: Session,
    survey_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.SurveyAnswer]:
    """
    获取指定调研的所有答案，支持分页
    
    Args:
        db: 数据库会话
        survey_id: 调研ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.SurveyAnswer]: 答案列表
    """
    return db.query(models.SurveyAnswer).filter(
        models.SurveyAnswer.survey_id == survey_id
    ).offset(skip).limit(limit).all()

def get_survey_answer(db: Session, answer_id: int) -> Optional[models.SurveyAnswer]:
    """
    根据ID获取单个调研答案
    
    Args:
        db: 数据库会话
        answer_id: 答案ID
        
    Returns:
        Optional[models.SurveyAnswer]: 答案对象，如果不存在则返回None
    """
    return db.query(models.SurveyAnswer).filter(models.SurveyAnswer.id == answer_id).first()

# ===== Organization CRUD 操作 =====

def get_organization(db: Session, org_id: int) -> Optional[models.Organization]:
    """
    根据 ID 获取单个组织
    
    Args:
        db: 数据库会话
        org_id: 组织ID
        
    Returns:
        Optional[models.Organization]: 组织对象，如果不存在则返回None
    """
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organization_by_name(db: Session, name: str) -> Optional[models.Organization]:
    """
    根据组织名称获取组织
    
    Args:
        db: 数据库会话
        name: 组织名称
        
    Returns:
        Optional[models.Organization]: 组织对象，如果不存在则返回None
    """
    return db.query(models.Organization).filter(models.Organization.name == name).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    """
    获取所有组织列表，支持分页
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.Organization]: 组织列表
    """
    return db.query(models.Organization).offset(skip).limit(limit).all()

def get_public_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    """
    获取公开的组织列表，用于企业对比
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.Organization]: 公开的组织列表
    """
    return db.query(models.Organization).filter(
        models.Organization.is_active == True
    ).offset(skip).limit(limit).all()

def create_organization(db: Session, org: OrganizationCreate, owner_id: int) -> models.Organization:
    """
    创建新组织，并指定所有者
    
    Args:
        db: 数据库会话
        org: 组织创建数据
        owner_id: 所有者ID
        
    Returns:
        models.Organization: 创建的组织对象
    """
    try:
        org_data = org.dict()
        print(f"Creating organization with data: {org_data}")
        print(f"Owner ID: {owner_id}")
        
        db_org = models.Organization(
            name=org_data["name"],
            description=org_data.get("description"),
            owner_id=owner_id
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org
    except Exception as e:
        print(f"Error creating organization: {e}")
        db.rollback()
        raise

def update_organization(db: Session, org_id: int, org_update: OrganizationUpdate) -> Optional[models.Organization]:
    """
    更新组织信息
    
    Args:
        db: 数据库会话
        org_id: 组织ID
        org_update: 组织更新数据
        
    Returns:
        Optional[models.Organization]: 更新后的组织对象，如果组织不存在则返回None
    """
    db_org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if db_org:
        update_data = org_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_org, key, value)
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
    return db_org

def delete_organization(db: Session, org_id: int) -> Optional[models.Organization]:
    """
    删除组织
    
    Args:
        db: 数据库会话
        org_id: 组织ID
        
    Returns:
        Optional[models.Organization]: 被删除的组织对象，如果组织不存在则返回None
    """
    db_org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if db_org:
        db.delete(db_org)
        db.commit()
    return db_org

# ===== Organization Member CRUD 操作 =====

def get_organization_member(db: Session, member_id: int) -> Optional[models.OrganizationMember]:
    """
    根据 ID 获取单个组织成员记录
    
    Args:
        db: 数据库会话
        member_id: 成员记录ID
        
    Returns:
        Optional[models.OrganizationMember]: 成员记录对象，如果不存在则返回None
    """
    return db.query(models.OrganizationMember).filter(models.OrganizationMember.id == member_id).first()

def get_organization_member_by_org_and_user(db: Session, organization_id: int, user_id: int) -> Optional[models.OrganizationMember]:
    """
    获取特定组织中特定用户的成员记录
    
    Args:
        db: 数据库会话
        organization_id: 组织ID
        user_id: 用户ID
        
    Returns:
        Optional[models.OrganizationMember]: 成员记录对象，如果不存在则返回None
    """
    return db.query(models.OrganizationMember).filter(
        models.OrganizationMember.organization_id == organization_id,
        models.OrganizationMember.user_id == user_id
    ).first()

def get_organization_members_by_organization(db: Session, organization_id: int, skip: int = 0, limit: int = 100) -> List[models.OrganizationMember]:
    """
    获取某个组织的所有成员，支持分页
    
    Args:
        db: 数据库会话
        organization_id: 组织ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.OrganizationMember]: 成员记录列表
    """
    return db.query(models.OrganizationMember).filter(
        models.OrganizationMember.organization_id == organization_id
    ).offset(skip).limit(limit).all()

def get_organizations_by_user_membership(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.OrganizationMember]:
    """
    获取某个用户所属的所有组织成员记录，支持分页
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.OrganizationMember]: 成员记录列表
    """
    return db.query(models.OrganizationMember).filter(
        models.OrganizationMember.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_organization_member(db: Session, member: OrganizationMemberCreate) -> models.OrganizationMember:
    """
    创建新的组织成员记录
    
    Args:
        db: 数据库会话
        member: 成员创建数据
        
    Returns:
        models.OrganizationMember: 创建的成员记录对象
    """
    db_member = models.OrganizationMember(
        **member.dict()
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_organization_member(db: Session, member_id: int, member_update: OrganizationMemberUpdate) -> Optional[models.OrganizationMember]:
    """
    更新组织成员信息（例如角色）
    
    Args:
        db: 数据库会话
        member_id: 成员记录ID
        member_update: 成员更新数据
        
    Returns:
        Optional[models.OrganizationMember]: 更新后的成员记录对象，如果记录不存在则返回None
    """
    db_member = db.query(models.OrganizationMember).filter(models.OrganizationMember.id == member_id).first()
    if db_member:
        update_data = member_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_member, key, value)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
    return db_member

def delete_organization_member(db: Session, member_id: int) -> Optional[models.OrganizationMember]:
    """
    删除组织成员记录
    
    Args:
        db: 数据库会话
        member_id: 成员记录ID
        
    Returns:
        Optional[models.OrganizationMember]: 被删除的成员记录对象，如果记录不存在则返回None
    """
    db_member = db.query(models.OrganizationMember).filter(models.OrganizationMember.id == member_id).first()
    if db_member:
        db.delete(db_member)
        db.commit()
    return db_member

# ===== Category CRUD 操作 =====

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """
    根据ID获取单个分类
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        
    Returns:
        Optional[models.Category]: 分类对象，如果不存在则返回None
    """
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories(db: Session, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """
    获取分类列表，支持分页和按组织筛选
    
    Args:
        db: 数据库会话
        organization_id: 组织ID，为空表示获取全局分类
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[models.Category]: 分类列表
    """
    query = db.query(models.Category)
    if organization_id is not None:
        query = query.filter(models.Category.organization_id == organization_id)
    else:
        query = query.filter(models.Category.organization_id.is_(None))
    
    return query.offset(skip).limit(limit).all()

def get_category_tree(db: Session, organization_id: Optional[int] = None) -> List[models.Category]:
    """
    获取分类树结构
    
    Args:
        db: 数据库会话
        organization_id: 组织ID，为空表示获取全局分类树
        
    Returns:
        List[models.Category]: 分类树列表
    """
    query = db.query(models.Category)
    if organization_id is not None:
        query = query.filter(models.Category.organization_id == organization_id)
    else:
        query = query.filter(models.Category.organization_id.is_(None))
    
    return query.filter(models.Category.parent_id.is_(None)).order_by(models.Category.sort_order).all()

def get_category_children(db: Session, parent_id: int) -> List[models.Category]:
    """
    获取指定分类的子分类
    
    Args:
        db: 数据库会话
        parent_id: 父分类ID
        
    Returns:
        List[models.Category]: 子分类列表
    """
    return db.query(models.Category).filter(
        models.Category.parent_id == parent_id
    ).order_by(models.Category.sort_order).all()

def create_category(db: Session, category: CategoryCreate, created_by: int) -> models.Category:
    """
    创建新分类
    
    Args:
        db: 数据库会话
        category: 分类创建数据
        created_by: 创建者ID
        
    Returns:
        models.Category: 创建的分类对象
    """
    # 计算分类层级和路径
    level = 1
    path = None
    
    if category.parent_id:
        parent = get_category(db, category.parent_id)
        if parent:
            level = parent.level + 1
            path = f"{parent.path}/{parent.id}" if parent.path else str(parent.id)
    
    db_category = models.Category(
        **category.dict(),
        created_by=created_by,
        level=level,
        path=path
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[models.Category]:
    """
    更新分类信息
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        category_update: 分类更新数据
        
    Returns:
        Optional[models.Category]: 更新后的分类对象，如果不存在则返回None
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        update_data = category_update.dict(exclude_unset=True)
        
        # 如果更新了父分类，需要重新计算层级和路径
        if 'parent_id' in update_data:
            level = 1
            path = None
            
            if update_data['parent_id']:
                parent = get_category(db, update_data['parent_id'])
                if parent:
                    level = parent.level + 1
                    path = f"{parent.path}/{parent.id}" if parent.path else str(parent.id)
            
            update_data['level'] = level
            update_data['path'] = path
        
        for key, value in update_data.items():
            setattr(db_category, key, value)
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[models.Category]:
    """
    删除分类
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        
    Returns:
        Optional[models.Category]: 被删除的分类对象，如果不存在则返回None
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        # 检查是否有子分类
        children = get_category_children(db, category_id)
        if children:
            raise ValueError("无法删除有子分类的分类，请先删除子分类")
        
        # 检查是否有题目使用此分类
        questions_count = db.query(models.Question).filter(
            models.Question.category_id == category_id
        ).count()
        if questions_count > 0:
            raise ValueError(f"无法删除分类，有 {questions_count} 个题目正在使用此分类")
        
        db.delete(db_category)
        db.commit()
    return db_category

def get_category_question_count(db: Session, category_id: int) -> int:
    """
    获取分类下的题目数量
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        
    Returns:
        int: 题目数量
    """
    return db.query(models.Question).filter(
        models.Question.category_id == category_id
    ).count()

def move_category(db: Session, category_id: int, target_parent_id: Optional[int], position: Optional[int] = None) -> Optional[models.Category]:
    """
    移动分类到新的父分类下
    
    Args:
        db: 数据库会话
        category_id: 要移动的分类ID
        target_parent_id: 目标父分类ID，为空表示移动到顶级
        position: 在同级中的位置
        
    Returns:
        Optional[models.Category]: 移动后的分类对象
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        return None
    
    # 更新父分类
    db_category.parent_id = target_parent_id
    
    # 重新计算层级和路径
    level = 1
    path = None
    
    if target_parent_id:
        parent = get_category(db, target_parent_id)
        if parent:
            level = parent.level + 1
            path = f"{parent.path}/{parent.id}" if parent.path else str(parent.id)
    
    db_category.level = level
    db_category.path = path
    
    # 更新排序
    if position is not None:
        db_category.sort_order = position
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category