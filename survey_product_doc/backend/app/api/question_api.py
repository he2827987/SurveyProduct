# backend/app/api/question_api.py
"""
问题管理API模块
提供问卷问题创建、查询、更新、删除等功能的RESTful接口
支持问卷内问题和全局题库问题两种模式
"""

# ===== 导入依赖 =====
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, cast

from backend.app.database import get_db
from backend.app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse
from backend.app import crud
from backend.app.security import get_current_user
from backend.app import models, security

# ===== API路由器配置 =====
# 注意：这个路由器没有prefix，因为它的路径会由survey_api包含
router = APIRouter(
    tags=["Questions"]
)

# ===== 问卷内问题管理接口 =====

@router.post("/surveys/{survey_id}/questions/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question_for_survey(
    survey_id: int,
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    为指定问卷创建新问题
    
    权限要求：只有问卷的创建者才能添加问题
    
    Args:
        survey_id: 问卷ID
        question: 问题创建数据
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        QuestionResponse: 创建的问题对象
        
    Raises:
        HTTPException: 404 - 问卷未找到
        HTTPException: 403 - 无权限添加问题
    """
    # 检查问卷是否存在
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    # 检查当前用户是否是问卷的创建者
    user_id = current_user.id
    if db_survey.created_by_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权在此问卷中添加问题")

    return crud.create_survey_question(db=db, question=question, survey_id=survey_id)

@router.get("/surveys/{survey_id}/questions/", response_model=List[QuestionResponse])
def read_questions_for_survey(
    survey_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取指定问卷的所有问题，支持分页
    
    Args:
        survey_id: 问卷ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话
        
    Returns:
        List[QuestionResponse]: 问题列表
        
    Raises:
        HTTPException: 404 - 问卷未找到
    """
    # 检查问卷是否存在
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    questions = crud.get_questions_by_survey(db, survey_id=survey_id, skip=skip, limit=limit)
    return questions

# ===== 通用问题管理接口 =====

@router.get("/questions/{question_id}", response_model=QuestionResponse)
def read_question(question_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个问题
    
    Args:
        question_id: 问题ID
        db: 数据库会话
        
    Returns:
        QuestionResponse: 问题对象
        
    Raises:
        HTTPException: 404 - 问题未找到
    """
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题未找到")
    return db_question

@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_existing_question(
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    更新现有问题
    
    权限要求：只有问题所属问卷的创建者才能修改问题
    
    Args:
        question_id: 问题ID
        question_update: 问题更新数据
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        QuestionResponse: 更新后的问题对象
        
    Raises:
        HTTPException: 404 - 问题未找到
        HTTPException: 403 - 无权限修改问题
    """
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题未找到")

    # 权限检查：只有创建者可以修改题目
    if db_question.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此问题")

    updated_question = crud.update_question(db=db, question_id=question_id, question_update=question_update)
    return updated_question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    删除现有问题
    
    权限要求：
    - 全局题库题目：只有创建者(owner_id)可以删除
    - 问卷题目：只有问卷创建者(created_by_user_id)可以删除
    
    Args:
        question_id: 问题ID
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        dict: 空字典（204状态码不返回内容）
        
    Raises:
        HTTPException: 404 - 问题未找到
        HTTPException: 403 - 无权限删除问题
        HTTPException: 500 - 题目关联的问卷不存在
    """
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题未找到")

    # 权限检查：只有创建者可以删除题目
    if db_question.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此题目")

    crud.delete_question(db=db, question_id=question_id)
    # 204状态码通常不返回内容
    return {}

# ===== 全局题库管理接口 =====

@router.post("/questions/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_global_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    在全局题库中创建一个新问题
    
    Args:
        question: 问题创建数据
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        QuestionResponse: 创建的问题对象
    """
    # 调用CRUD函数创建问题
    db_question = crud.create_global_question(db=db, question=question, owner_id=current_user.id)
    return db_question

# ===== 组织题库管理接口 =====

@router.post("/organizations/{org_id}/questions/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_organization_question(
    org_id: int,
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    在组织题库中创建一个新问题
    
    Args:
        org_id: 组织ID
        question: 问题创建数据
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        QuestionResponse: 创建的问题对象
    """
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, org_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限管理该组织")
    
    # 调用CRUD函数创建组织问题
    db_question = crud.create_organization_question(db=db, question=question, owner_id=current_user.id, organization_id=org_id)
    return db_question

@router.get("/organizations/{org_id}/questions/", response_model=QuestionListResponse)
def read_organization_questions(
    org_id: int,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="按题目类型筛选 (single, multiple, text)"),
    search: Optional[str] = Query(None, description="搜索关键词，在题目文本中搜索"),
    sort_by: Optional[str] = Query(None, description="排序方式 (created_desc, created_asc, usage_desc, usage_asc)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    获取组织题库中的所有问题，支持分页和按类型筛选
    
    Args:
        org_id: 组织ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        type: 题目类型筛选参数
        db: 数据库会话
        current_user: 当前认证用户
        
    Returns:
        QuestionListResponse: 包含问题列表和分页信息的响应对象
    """
    # 检查用户是否有权限访问该组织
    if not has_organization_access(db, current_user, org_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限访问该组织")
    
    result = crud.get_organization_questions(db, org_id=org_id, skip=skip, limit=limit, type_filter=type, search_filter=search, sort_by=sort_by)
    return result

@router.get("/questions/", response_model=QuestionListResponse)
def read_global_questions(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="按题目类型筛选 (single_choice/multi_choice/text_input/number_input，也兼容 single/multiple/text/number)"),
    search: Optional[str] = Query(None, description="搜索关键词，在题目文本中搜索"),
    sort_by: Optional[str] = Query(None, description="排序方式 (created_desc, created_asc, usage_desc, usage_asc)"),
    category_id: Optional[int] = Query(None, description="按分类ID筛选"),
    tags: Optional[str] = Query(None, description="按标签筛选，多个标签用逗号分隔"),
    db: Session = Depends(get_db)
):
    """
    获取全局题库中的所有问题，支持分页和按类型筛选
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        type: 题目类型筛选参数
        db: 数据库会话
        
    Returns:
        QuestionListResponse: 包含问题列表和分页信息的响应对象
    """
    # 处理标签筛选参数
    tag_filter = None
    if tags:
        tag_filter = [tag.strip() for tag in tags.split(',') if tag.strip()]

    # 兼容前端旧枚举/别名
    type_alias_map = {
        "single": "single_choice",
        "multiple": "multi_choice",
        "text": "text_input",
        "number": "number_input",
    }
    if type in type_alias_map:
        type = type_alias_map[type]
    
    result = crud.get_global_questions(db, skip=skip, limit=limit, type_filter=type, search_filter=search, sort_by=sort_by, category_filter=category_id, tag_filter=tag_filter)
    return result

def has_organization_access(db: Session, user: models.User, org_id: int) -> bool:
    """检查用户是否有权限访问组织"""
    from backend.app.models.organization import Organization
    from backend.app.models.organization_member import OrganizationMember
    
    # 组织所有者
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org and org.owner_id == user.id:
        return True
    
    # 组织成员
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user.id
    ).first()
    
    return member is not None

def has_organization_manage_access(db: Session, user: models.User, org_id: int) -> bool:
    """检查用户是否有权限管理组织"""
    from backend.app.models.organization import Organization
    from backend.app.models.organization_member import OrganizationMember
    
    # 组织所有者
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org and org.owner_id == user.id:
        return True
    
    # 组织管理员
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user.id,
        OrganizationMember.role.in_(["owner", "admin"])
    ).first()
    
    return member is not None