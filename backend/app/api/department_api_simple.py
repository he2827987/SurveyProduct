# backend/app/api/department_api_simple.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.organization_member import OrganizationMember
from backend.app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
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
    print(f"DEBUG: department data: {department}")
    
    # 检查组织是否存在
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    print(f"DEBUG: Found organization: {org.name}")
    
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
    
    # 计算部门层级
    level = 1
    if department.parent_id:
        parent = db.query(Department).filter(
            Department.id == department.parent_id,
            Department.organization_id == org_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="上级部门不存在"
            )
        level = parent.level + 1
    
    print(f"DEBUG: Creating department with level={level}")
    
    new_department = Department(
        name=department.name,
        code=department.code,
        description=department.description,
        organization_id=org_id,
        parent_id=department.parent_id,
        level=level
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    
    print(f"DEBUG: Department created successfully: {new_department.name}")
    return new_department
