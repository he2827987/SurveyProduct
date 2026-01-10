
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.api.deps import get_db
from backend.app.security import get_current_user
from backend.app.models.user import User as UserModel
from backend.app.services.statistics_service import get_survey_stats_by_dimension, get_per_question_scores, get_line_scores_by_dimension, get_pie_option_distribution
from backend.app.services.chart_service import get_question_option_stats

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

@router.get("/survey/{survey_id}/stats", response_model=Dict[str, Any])
def get_survey_analysis_stats(
    survey_id: int,
    dimension: str,
    organizations: Optional[List[int]] = Query(None, description="按组织ID过滤/对比"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取调研统计数据（按维度分组）
    dimension: 'department' | 'position'
    """
    if dimension not in ["department", "position", "organization"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dimension. Must be 'department', 'position' or 'organization'."
        )
    stats = get_survey_stats_by_dimension(db, survey_id, dimension, organization_ids=organizations)
    return {
        "dimension": dimension,
        "stats": stats
    }


@router.get("/survey/{survey_id}/questions/scores", response_model=List[Dict[str, Any]])
def get_question_scores(
    survey_id: int,
    department: Optional[str] = None,
    position: Optional[str] = None,
    organizations: Optional[List[int]] = Query(None, description="按组织过滤"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    按题目汇总总分/平均分，支持部门或职位过滤
    """
    scores = get_per_question_scores(db, survey_id, department=department, position=position, organization_ids=organizations)
    return scores

@router.get("/survey/{survey_id}/charts/options", response_model=List[Dict[str, Any]])
def get_survey_option_charts(
    survey_id: int,
    dimension: str = "department",
    organizations: Optional[List[int]] = Query(None, description="按组织过滤/对比"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取选项分布图表数据（按维度构成）
    """
    if dimension not in ["department", "position", "organization"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dimension")
    charts = get_question_option_stats(db, survey_id, dimension=dimension, organization_ids=organizations)
    return charts



@router.get("/survey/{survey_id}/line", response_model=Dict[str, Any])
def get_line_scores(
    survey_id: int,
    dimension: str = "department",
    scope: str = "survey",
    question_ids: Optional[List[int]] = Query(None, description="指定题目ID列表，scope=question 时生效"),
    organizations: Optional[List[int]] = Query(None, description="按组织过滤/对比"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取折线图数据：X轴为人群（部门/职位），Y轴为平均分。
    scope = survey 时返回问卷总分；scope = question 时返回指定题目的平均分；
    可以同时请求问卷总分与题目均分（scope=question，include_survey_total=true 可扩展）。
    """
    if dimension not in ["department", "position", "organization"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dimension")

    include_survey_total = False
    if scope == "survey":
        include_survey_total = True
        question_ids = []
    elif scope == "question":
        include_survey_total = False
    elif scope == "both":
        include_survey_total = True
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scope")

    try:
        result = get_line_scores_by_dimension(
            db,
            survey_id=survey_id,
            dimension=dimension,
            question_ids=question_ids,
            include_survey_total=include_survey_total,
            organization_ids=organizations
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return result


@router.get("/survey/{survey_id}/pie", response_model=Dict[str, Any])
def get_pie_distribution(
    survey_id: int,
    question_id: int = Query(..., description="题目ID"),
    option_text: str = Query(..., description="选项文本，未作答可传'(未作答)'") ,
    dimension: str = "department",
    include_unanswered: bool = True,
    organizations: Optional[List[int]] = Query(None, description="按组织过滤/对比"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取饼图数据：某题某选项在不同部门/职位/组织下的选择分布。"""
    if dimension not in ["department", "position", "organization"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dimension")
    try:
        result = get_pie_option_distribution(
            db,
            survey_id=survey_id,
            question_id=question_id,
            option_text=option_text,
            dimension=dimension,
            include_unanswered=include_unanswered,
            organization_ids=organizations
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result
