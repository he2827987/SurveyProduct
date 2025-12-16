# backend/app/api/department_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
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
    # 检查用户是否有权限访问该组织
    if not has_organization_access(db, current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问该组织"
        )
    
    departments = db.query(Department).filter(
        Department.organization_id == org_id,
        Department.is_active == True
    ).all()
    
    return departments

@router.get("/organizations/{org_id}/departments/public", response_model=List[DepartmentResponse])
def get_public_departments(
    org_id: int,
    db: Session = Depends(get_db),
):
    """获取公开的组织部门列表（无需认证）"""
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
    return departments

@router.get("/organizations/{org_id}/departments/tree", response_model=List[DepartmentResponse])
def get_department_tree(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取组织的部门树结构"""
    # 检查用户是否有权限访问该组织
    if not has_organization_access(db, current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问该组织"
        )
    
    # 获取顶级部门
    root_departments = db.query(Department).filter(
        Department.organization_id == org_id,
        Department.parent_id == None,
        Department.is_active == True
    ).all()
    
    return build_department_tree(root_departments, db)

@router.post("/organizations/{org_id}/departments", response_model=DepartmentResponse)
def create_department(
    org_id: int,
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建部门"""
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
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
    
    return new_department

@router.put("/departments/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新部门"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, dept.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
        )
    
    # 检查部门编码是否重复
    if department.code and department.code != dept.code:
        existing_dept = db.query(Department).filter(
            Department.organization_id == dept.organization_id,
            Department.code == department.code,
            Department.id != dept_id,
            Department.is_active == True
        ).first()
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门编码已存在"
            )
    
    # 更新部门信息
    for field, value in department.dict(exclude_unset=True).items():
        setattr(dept, field, value)
    
    db.commit()
    db.refresh(dept)
    
    return dept

@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除部门"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查用户是否有权限管理该组织
    if not has_organization_manage_access(db, current_user, dept.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限管理该组织"
        )
    
    # 软删除部门及其子部门
    delete_department_recursive(dept_id, db)
    
    return {"message": "部门删除成功"}

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

def build_department_tree(departments: List[Department], db: Session) -> List[Department]:
    """构建部门树结构"""
    result = []
    for dept in departments:
        dept_dict = {
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "level": dept.level,
            "parent_id": dept.parent_id,
            "organization_id": dept.organization_id,
            "is_active": dept.is_active,
            "created_at": dept.created_at,
            "updated_at": dept.updated_at,
            "children": []
        }
        
        # 获取子部门
        children = db.query(Department).filter(
            Department.parent_id == dept.id,
            Department.is_active == True
        ).all()
        
        if children:
            dept_dict["children"] = build_department_tree(children, db)
        
        result.append(dept_dict)
    
    return result

def delete_department_recursive(dept_id: int, db: Session):
    """递归删除部门及其子部门"""
    # 获取子部门
    children = db.query(Department).filter(Department.parent_id == dept_id).all()
    
    # 递归删除子部门
    for child in children:
        delete_department_recursive(child.id, db)
    
    # 软删除当前部门
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if dept:
        dept.is_active = False
        db.commit()
