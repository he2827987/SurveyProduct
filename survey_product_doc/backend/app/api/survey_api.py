# backend/app/api/survey_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, cast

from backend.app.api.deps import get_db
from backend.app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyResponse, SurveyStatusUpdate, SubjectiveAnswerDetail
from backend.app import crud
from backend.app.security import get_current_user
from backend.app.services import survey_service
from backend.app.models.user import User as UserModel
from backend.app.models.survey import Survey as SurveyModel

router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"]
)

@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
def create_survey(
    survey: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    创建一个新的问卷。
    需要用户认证。
    """
    return survey_service.create_survey(db=db, survey=survey, user_id=cast(int, current_user.id))

@router.get("/{survey_id}", response_model=SurveyResponse)
def get_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # 确保用户已认证
):
    """
    根据 ID 获取单个问卷。
    只有问卷的创建者才能访问。
    """
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    # 权限检查：只有问卷的创建者才能获取问卷详情
    if cast(int, db_survey.created_by_user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此问卷")

    return db_survey

@router.get("/", response_model=List[SurveyResponse])
def get_user_surveys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取当前用户创建的所有问卷。
    需要用户认证。
    """
    surveys = survey_service.get_surveys_by_user(db=db, user_id=cast(int, current_user.id), skip=skip, limit=limit)
    return surveys

@router.get("/global/all", response_model=List[SurveyResponse])
def get_global_surveys(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取全局调研库中的所有调研。
    所有用户都可以查看，但只有创建者可以编辑。
    """
    surveys = survey_service.get_global_surveys(
        db=db, 
        skip=skip, 
        limit=limit, 
        search=search,
        status_filter=status_filter,
        sort_by=sort_by
    )
    return surveys

@router.put("/{survey_id}", response_model=SurveyResponse)
def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新指定 ID 的问卷。
    只有问卷的创建者才能更新。
    """
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    # 权限检查：只有问卷的创建者才能更新问卷
    if cast(int, db_survey.created_by_user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新此问卷")

    updated_survey = survey_service.update_survey(db=db, survey_id=survey_id, survey_update=survey_update)
    return updated_survey


@router.post("/{survey_id}/status", response_model=SurveyResponse)
def update_survey_status(
    survey_id: int,
    status_update: SurveyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")
    if cast(int, db_survey.created_by_user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新该问卷状态")

    survey_service.update_survey_status(
        db=db,
        survey_id=survey_id,
        status=status_update.status,
        end_time=status_update.end_time,
        start_time=status_update.start_time
    )

    updated = survey_service.get_survey(db=db, survey_id=survey_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")
    return updated

@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    删除指定 ID 的问卷。
    只有问卷的创建者才能删除。
    """
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    # 权限检查：只有问卷的创建者才能删除问卷
    if cast(int, db_survey.created_by_user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此问卷")

    survey_service.delete_survey(db=db, survey_id=survey_id)
    return {"message": "问卷删除成功"} # FastAPI 204 No Content 响应通常不返回内容，但为了清晰可以返回消息

# ===== 移动端调研填写API（公开访问，无需认证） =====

@router.get("/{survey_id}/fill")
def get_survey_for_filling(survey_id: int, db: Session = Depends(get_db)):
    """
    获取用于填写的调研内容（公开信息，无需认证）
    """
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="调研未找到")
    
    # 返回公开的调研信息
    return {
        "id": db_survey.id,
        "title": db_survey.title,
        "description": db_survey.description,
        "status": db_survey.status,
        "organization_id": db_survey.organization_id
    }

@router.get("/{survey_id}/questions")
def get_survey_questions(survey_id: int, db: Session = Depends(get_db)):
    """
    获取调研的题目列表（公开访问，无需认证）
    """
    # 检查调研是否存在
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="调研未找到")
    
    # 获取调研的题目
    questions = survey_service.get_survey_questions(db=db, survey_id=survey_id)
    if questions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="调研题目未找到")
    
    return questions


@router.get("/{survey_id}/subjective-answers", response_model=List[SubjectiveAnswerDetail])
def get_subjective_answers(
    survey_id: int,
    question_id: Optional[int] = None,
    question_number: Optional[int] = None,
    question_text: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    survey = crud.get_survey(db, survey_id=survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问卷未找到")

    if survey.organization_id and current_user.organization_id != survey.organization_id and cast(int, survey.created_by_user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能查看所属组织的主观答案")

    answers = survey_service.get_subjective_answers(
        db=db,
        survey_id=survey_id,
        question_id=question_id,
        question_number=question_number,
        question_text=question_text,
        department=department
    )

    return answers

@router.get("/{survey_id}/detail")
def get_survey_detail(survey_id: int, db: Session = Depends(get_db)):
    """
    获取调研详情（公开访问，无需认证）
    包含基本信息和题目列表
    """
    # 检查调研是否存在
    db_survey = survey_service.get_survey(db=db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="调研未找到")
    
    # 获取调研的题目
    questions = survey_service.get_survey_questions(db=db, survey_id=survey_id)
    
    # 返回调研详情（包含题目）
    return {
        "id": db_survey.id,
        "title": db_survey.title,
        "description": db_survey.description,
        "status": db_survey.status,
        "created_at": db_survey.created_at,
        "updated_at": db_survey.updated_at,
        "organization_id": db_survey.organization_id,
        "questions": questions or []
    }
