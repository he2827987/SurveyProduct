# backend/app/api/department_api_minimal.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.schemas.department import DepartmentCreate, DepartmentResponse
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/organizations/{org_id}/departments", response_model=List[DepartmentResponse])
def get_departments(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取组织的部门列表"""
    print(f"DEBUG: get_departments called for org_id={org_id}")
    
    # 简单检查组织是否存在
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    departments = db.query(Department).filter(
        Department.organization_id == org_id,
        Department.is_active == True
    ).all()
    
    print(f"DEBUG: Found {len(departments)} departments")
    return departments

@router.post("/organizations/{org_id}/departments", response_model=DepartmentResponse)
def create_department(
    org_id: int,
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建部门"""
    print(f"DEBUG: create_department called for org_id={org_id}")
    
    # 简单检查组织是否存在
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    # 检查部门编码是否重复
    if department.code:
        existing_dept = db.query(Department).filter(
            Department.organization_id == org_id,
            Department.code == department.code,
            Department.is_active == True
        ).first()
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门编码已存在"
            )
    
    # 创建部门
    new_department = Department(
        name=department.name,
        code=department.code,
        description=department.description,
        organization_id=org_id,
        level=1
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    
    print(f"DEBUG: Department created successfully: {new_department.name}")
    return new_department
