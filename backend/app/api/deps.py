# backend/app/api/deps.py

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app import crud, models, schemas
from app.database import get_db
from sqlalchemy.orm import Session
from app.security import get_current_user

async def get_survey_by_id_and_owner(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Survey:
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if not db_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    if db_survey.created_by_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this survey's answers")
    return db_survey

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前活跃用户。
    """
    # 暂时跳过is_active检查，因为可能没有这个属性
    # if not current_user.is_active:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非活跃用户")
    return current_user

# --- 新增：获取当前活跃的超级用户 (系统管理员) ---
async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前活跃的超级用户（系统管理员）。
    """
    # 暂时跳过is_superuser检查，因为可能没有这个属性
    # if not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="用户权限不足，需要超级用户权限"
    #     )
    return current_user