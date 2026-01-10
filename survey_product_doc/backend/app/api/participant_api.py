# backend/app/api/participant_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.participant import Participant
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.organization_member import OrganizationMember
from backend.app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/organizations/{org_id}/participants", response_model=List[ParticipantResponse])
def get_participants(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取组织的参与者列表"""
    # 检查用户是否有权限访问该组织
    if not has_organization_access(db, current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问该组织"
        )
    
    participants = db.query(Participant).filter(
        Participant.organization_id == org_id
    ).all()
    
    return participants

@router.post("/organizations/{org_id}/participants", response_model=ParticipantResponse)
def create_participant(
    org_id: int,
    participant: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建参与者"""
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
        )
    
    # 检查部门是否存在且属于该组织
    if participant.department_id:
        from backend.app.models.department import Department
        dept = db.query(Department).filter(
            Department.id == participant.department_id,
            Department.organization_id == org_id,
            Department.is_active == True
        ).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门不存在或不属于该组织"
            )
    
    new_participant = Participant(
        name=participant.name,
        department_id=participant.department_id,
        position=participant.position,
        email=participant.email,
        phone=participant.phone,
        organization_id=org_id
    )
    
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    
    return new_participant

@router.put("/participants/{participant_id}", response_model=ParticipantResponse)
def update_participant(
    participant_id: int,
    participant: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新参与者信息"""
    participant_obj = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参与者不存在"
        )
    
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, participant_obj.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
        )
    
    # 检查部门是否存在且属于该组织
    if participant.department_id:
        from backend.app.models.department import Department
        dept = db.query(Department).filter(
            Department.id == participant.department_id,
            Department.organization_id == participant_obj.organization_id,
            Department.is_active == True
        ).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门不存在或不属于该组织"
            )
    
    # 更新参与者信息
    for field, value in participant.dict(exclude_unset=True).items():
        setattr(participant_obj, field, value)
    
    db.commit()
    db.refresh(participant_obj)
    
    return participant_obj

@router.delete("/participants/{participant_id}")
def delete_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除参与者"""
    participant_obj = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参与者不存在"
        )
    
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, participant_obj.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
        )
    
    db.delete(participant_obj)
    db.commit()
    
    return {"message": "参与者删除成功"}

def has_organization_access(db: Session, user: User, org_id: int) -> bool:
    """检查用户是否有权限访问组织"""
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

def has_organization_manage_access(db: Session, user: User, org_id: int) -> bool:
    """检查用户是否有权限管理组织"""
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
