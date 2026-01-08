# backend/app/api/answer_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, cast
import json

from backend.app import crud, schemas, models
from backend.app.api.deps import get_db, get_survey_by_id_and_owner
from backend.app.security import get_current_user, get_current_user_optional
from fastapi.security import HTTPBearer
from fastapi import Header

router = APIRouter() # 路由前缀将在 main.py 中定义

# 提交问卷回答（支持匿名访问）
@router.post(
    "/surveys/{survey_id}/answers/",
    response_model=schemas.SurveyAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer to a survey (anonymous allowed)"
)
async def submit_survey_answer(
    survey_id: int,
    answer_in: schemas.SurveyAnswerCreate, # 使用 answer_in 避免与 crud 函数的 answer 参数混淆
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None) # 可选的认证头
):
    # 处理可选的用户认证
    current_user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            from backend.app.security import verify_token
            from backend.app.services import user_service
            payload = verify_token(token)
            if payload:
                username = payload.get("sub")
                if username:
                    current_user = user_service.get_user_by_username(db, username=username)
        except Exception:
            pass  # 忽略认证错误，允许匿名访问
    # 检查问卷是否存在
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")

    user_id: Optional[int] = None
    if current_user:
        user_id = cast(int, current_user.id)

    # 创建参与者（如果是匿名回答）
    participant_id = None
    # 补充默认组织ID：优先提交值，其次问卷组织，再其次当前用户
    if not getattr(answer_in, "organization_id", None):
        if db_survey.organization_id:
            answer_in.organization_id = db_survey.organization_id
        elif current_user and getattr(current_user, "organization_id", None):
            answer_in.organization_id = current_user.organization_id

    if not current_user and hasattr(answer_in, 'respondent_name') and answer_in.respondent_name:
        from backend.app.models.participant import Participant
        
        # 获取组织ID（从调研或提交数据中）
        organization_id = getattr(answer_in, 'organization_id', None)
        if not organization_id and db_survey.organization_id:
            organization_id = db_survey.organization_id
        
        if organization_id:
            # 创建参与者
            participant = Participant(
                name=answer_in.respondent_name,
                department_id=getattr(answer_in, 'department_id', None),
                position=getattr(answer_in, 'position', None),
                organization_id=organization_id
            )
            db.add(participant)
            db.commit()
            db.refresh(participant)
            participant_id = participant.id

    # 创建调研答案
    db_answer = crud.create_survey_answer(db, answer_in, survey_id, user_id, participant_id)

    # 返回前将 answers 字段从 JSON 字符串解析回字典
    db_answer.answers = json.loads(cast(str, db_answer.answers))
    return db_answer

# 获取某个问卷的所有回答 (只有问卷所有者可以查看)
@router.get(
    "/surveys/{survey_id}/answers/",
    response_model=List[schemas.SurveyAnswerResponse],
    summary="Get all answers for a specific survey (owner only)"
)
async def get_survey_answers(
    survey_id: int,
    db: Session = Depends(get_db),
    survey: models.Survey = Depends(get_survey_by_id_and_owner), # 这个依赖会处理 404 和 403
    skip: int = 0,
    limit: int = 100
):
    answers = crud.get_survey_answers_by_survey_id(db, survey_id, skip=skip, limit=limit)
    # 遍历 answers，将 answers 字段从 JSON 字符串解析回字典
    for ans in answers:
        ans.answers = json.loads(cast(str, ans.answers))
    return answers

# 获取单个回答 (只有问卷所有者或回答提交者可以查看)
@router.get(
    "/answers/{answer_id}", # 这个路由不包含 survey_id，直接通过 answer_id 获取
    response_model=schemas.SurveyAnswerResponse,
    summary="Get a single survey answer by ID (owner or submitter only)"
)
async def get_single_survey_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # 确保用户已登录
):
    db_answer = crud.get_survey_answer(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")

    # 检查当前用户是否是问卷的所有者 或 回答提交者
    db_survey = crud.get_survey(db, survey_id=cast(int, db_answer.survey_id))
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated survey not found")

    is_owner = cast(int, db_survey.owner_id) == cast(int, current_user.id)
    is_submitter = False
    if db_answer.user_id is not None: # 只有当回答有 user_id 时才检查
        is_submitter = cast(int, db_answer.user_id) == cast(int, current_user.id)
        
    if not (is_owner or is_submitter):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this answer")

    # 返回前将 answers 字段从 JSON 字符串解析回字典
    db_answer.answers = json.loads(cast(str, db_answer.answers))
    return db_answer
