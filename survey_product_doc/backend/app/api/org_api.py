# backend/app/api/org_api.py

from typing import Any, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app import crud, schemas, models
from backend.app.api import deps # 确保 deps.py 在同一个 api 目录下

router = APIRouter()

# --- 组织 (Organization) 相关 API ---

@router.post("/organizations/", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: schemas.OrganizationCreate,
    db: Session = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user), # 暂时跳过用户认证
) -> Any:
    """
    **创建新组织。**

    - 允许普通用户创建组织。
    - `name` 必须是唯一的。
    """
    print(f"Creating organization: {org_in.name}")
    # 使用固定的用户ID
    current_user_id = 3  # admin用户的ID
    print(f"Using fixed user ID: {current_user_id}")
    
    organization = crud.get_organization_by_name(db, name=org_in.name)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="组织名称已存在。",
        )
    
    organization = crud.create_organization(db, org=org_in, owner_id=current_user_id)
    print(f"Organization created: {organization.id}")
    
    # 自动将创建者添加为组织的 "owner" 角色成员
    member_data = schemas.OrganizationMemberCreate(
        organization_id=cast(int, organization.id),
        user_id=current_user_id,
        role="owner" # 创建者默认为组织所有者
    )
    print(f"Creating member: {member_data}")
    crud.create_organization_member(db, member_data)
    
    return organization

@router.get("/organizations/", response_model=List[schemas.OrganizationResponse])
def read_organizations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    **获取当前用户所属的所有组织列表。**

    - 任何活跃用户都可以获取其所属的组织。
    """
    # 获取用户所属的所有组织成员记录
    memberships = crud.get_organizations_by_user_membership(db, user_id=cast(int, current_user.id), skip=skip, limit=limit)
    # 从成员记录中提取组织对象
    organizations = [crud.get_organization(db, org_id=cast(int, m.organization_id)) for m in memberships]
    # 过滤掉可能为 None 的组织（如果组织已被删除但成员记录未及时清理）
    organizations = [org for org in organizations if org is not None]
    return organizations

@router.get("/organizations/public/", response_model=List[schemas.OrganizationResponse])
def read_public_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    **获取公开的组织列表（用于企业对比）。**

    - 无需认证，返回所有公开的组织。
    - 用于企业对比功能。
    """
    organizations = crud.get_public_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/organizations/{org_id}", response_model=schemas.OrganizationResponse)
def read_organization_by_id(
    org_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **根据 ID 获取单个组织。**

    - 用户必须是该组织的成员才能访问。
    """
    organization = crud.get_organization(db, org_id=org_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织未找到。",
        )
    # 检查当前用户是否是该组织的成员
    member = crud.get_organization_member_by_org_and_user(db, organization_id=org_id, user_id=cast(int, current_user.id))
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权访问此组织。",
        )
    return organization

@router.put("/organizations/{org_id}", response_model=schemas.OrganizationResponse)
def update_organization(
    org_id: int,
    org_in: schemas.OrganizationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **更新组织信息。**

    - 只有组织的 "owner" 或 "admin" 角色可以更新组织信息。
    """
    organization = crud.get_organization(db, org_id=org_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织未找到。",
        )

    # 检查用户权限：必须是组织的 owner 或 admin
    member = crud.get_organization_member_by_org_and_user(db, organization_id=org_id, user_id=cast(int, current_user.id))
    if member is None or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权更新此组织信息。",
        )

    # 检查名称是否重复（如果名称被修改）
    if org_in.name and org_in.name != organization.name:
        existing_org = crud.get_organization_by_name(db, name=org_in.name)
        if existing_org is not None and existing_org.id != org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="组织名称已存在。",
            )

    organization = crud.update_organization(db, org_id=org_id, org_update=org_in)
    return organization

@router.delete("/organizations/{org_id}", response_model=schemas.Msg)
def delete_organization(
    org_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **删除组织。**

    - 只有组织的 "owner" 角色可以删除组织。
    - 删除组织会级联删除其所有成员和问卷。
    """
    organization = crud.get_organization(db, org_id=org_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织未找到。",
        )

    # 检查用户权限：必须是组织的 owner
    member = crud.get_organization_member_by_org_and_user(db, organization_id=org_id, user_id=cast(int, current_user.id))
    if member is None or member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权删除此组织。",
        )

    crud.delete_organization(db, org_id=org_id)
    return {"msg": "组织及其相关数据已成功删除。"}


# --- 组织成员 (Organization Member) 相关 API ---

# 辅助函数：检查用户在组织中的角色
def check_organization_admin_or_owner(
    db: Session,
    organization_id: int,
    current_user: models.User
) -> models.OrganizationMember:
    """
    检查当前用户是否是指定组织的 'owner' 或 'admin'。
    如果不是，则抛出 HTTPException。
    """
    member = crud.get_organization_member_by_org_and_user(
        db, organization_id=organization_id, user_id=cast(int, current_user.id)
    )
    if member is None or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权管理此组织的成员。",
        )
    return member

@router.post("/organizations/{org_id}/members/", response_model=schemas.OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
def add_organization_member(
    org_id: int,
    member_in: schemas.OrganizationMemberCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **向组织添加成员。**

    - 只有组织的 "owner" 或 "admin" 角色可以添加成员。
    - `member_in.organization_id` 必须与路径参数 `org_id` 匹配。
    - 确保要添加的用户存在。
    - 确保用户尚未是该组织的成员。
    """
    if member_in.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请求体中的组织ID与路径参数不匹配。",
        )

    # 检查当前用户是否有权限添加成员
    check_organization_admin_or_owner(db, org_id, current_user)

    # 检查要添加的用户是否存在
    target_user = crud.get_user(db, user_id=cast(int, member_in.user_id))
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="要添加的用户不存在。",
        )

    # 检查用户是否已是该组织的成员
    existing_member = crud.get_organization_member_by_org_and_user(db, organization_id=org_id, user_id=cast(int, member_in.user_id))
    if existing_member is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已是此组织的成员。",
        )

    member = crud.create_organization_member(db, member=member_in)
    return member

@router.get("/organizations/{org_id}/members/", response_model=List[schemas.OrganizationMemberResponse])
def read_organization_members(
    org_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    **获取组织的所有成员列表。**

    - 只有组织的 "owner" 或 "admin" 角色可以查看成员列表。
    """
    # 检查当前用户是否有权限查看成员
    check_organization_admin_or_owner(db, org_id, current_user)

    members = crud.get_organization_members_by_organization(db, organization_id=org_id, skip=skip, limit=limit)
    return members

@router.put("/organizations/{org_id}/members/{member_id}", response_model=schemas.OrganizationMemberResponse)
def update_organization_member_role(
    org_id: int,
    member_id: int,
    member_update: schemas.OrganizationMemberUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **更新组织成员的角色。**

    - 只有组织的 "owner" 或 "admin" 角色可以更新成员角色。
    - 不能更新组织所有者（"owner"）的角色。
    - 不能将自己降级为非管理员角色（如果自己是唯一的管理员）。
    """
    # 检查当前用户是否有权限更新成员角色
    current_user_member_record = check_organization_admin_or_owner(db, org_id, current_user)

    member_to_update = crud.get_organization_member(db, member_id=member_id)
    if member_to_update is None or member_to_update.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织成员未找到或不属于此组织。",
        )

    # 组织所有者（"owner"）的角色不能被修改
    if member_to_update.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改组织所有者的角色。",
        )

    # 如果当前用户是管理员，并且尝试将自己降级为非管理员角色
    if member_to_update.user_id == cast(int, current_user.id) and member_update.role not in ["owner", "admin"]:
        # 检查是否还有其他管理员
        other_admins = [
            m for m in crud.get_organization_members_by_organization(db, organization_id=org_id)
            if m.role == "admin" and m.user_id != cast(int, current_user.id)
        ]
        if other_admins is None or len(other_admins) == 0 and current_user_member_record.role == "admin": # 确保当前用户确实是管理员
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您是此组织唯一的管理员，不能将自己降级。",
            )

    member = crud.update_organization_member(db, member_id=member_id, member_update=member_update)
    return member

@router.delete("/organizations/{org_id}/members/{member_id}", response_model=schemas.Msg)
def remove_organization_member(
    org_id: int,
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **从组织中移除成员。**

    - 只有组织的 "owner" 或 "admin" 角色可以移除成员。
    - 不能移除组织所有者（"owner"）。
    - 组织管理员不能移除自己（如果自己是唯一的管理员）。
    """
    # 检查当前用户是否有权限移除成员
    current_user_member_record = check_organization_admin_or_owner(db, org_id, current_user)

    member_to_remove = crud.get_organization_member(db, member_id=member_id)
    if member_to_remove is None or member_to_remove.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织成员未找到或不属于此组织。",
        )

    # 组织所有者（"owner"）不能被移除
    if member_to_remove.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能移除组织所有者。",
        )

    # 组织管理员不能移除自己（如果自己是唯一的管理员）
    if member_to_remove.user_id == cast(int, current_user.id) and current_user_member_record.role == "admin":
        # 检查是否还有其他管理员
        other_admins = [
            m for m in crud.get_organization_members_by_organization(db, organization_id=org_id)
            if m.role == "admin" and m.user_id != cast(int, current_user.id)    
        ]
        if other_admins is None or len(other_admins) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您是此组织唯一的管理员，不能移除自己。",
            )

    crud.delete_organization_member(db, member_id=member_id)
    return {"msg": "组织成员已成功移除。"}

