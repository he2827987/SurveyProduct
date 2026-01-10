# backend/app/api/category_api.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, 
    CategoryTreeResponse, CategoryMoveRequest, CategoryBulkUpdateRequest
)
from backend.app.crud import (
    get_category, get_categories, get_category_tree, create_category,
    update_category, delete_category, get_category_question_count,
    move_category, get_category_children
)
from backend.app.api.deps import get_current_active_user
from backend.app.models.organization_member import OrganizationMember

router = APIRouter()

def has_organization_access(db: Session, user_id: int, organization_id: int) -> bool:
    """检查用户是否有组织访问权限"""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id
    ).first()
    return member is not None

def has_organization_manage_access(db: Session, user_id: int, organization_id: int) -> bool:
    """检查用户是否有组织管理权限"""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id,
        OrganizationMember.role.in_(["admin", "manager"])
    ).first()
    return member is not None

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories_list(
    organization_id: Optional[int] = Query(None, description="组织ID，为空表示获取全局分类"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取分类列表"""
    # 如果指定了组织ID，检查权限
    if organization_id and not has_organization_access(db, current_user.id, organization_id):
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    categories = get_categories(db, organization_id, skip, limit)
    
    # 为每个分类添加题目数量
    result = []
    for category in categories:
        question_count = get_category_question_count(db, category.id)
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "code": category.code,
            "parent_id": category.parent_id,
            "sort_order": category.sort_order,
            "is_active": category.is_active,
            "level": category.level,
            "path": category.path,
            "organization_id": category.organization_id,
            "created_by": category.created_by,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "children": [],
            "question_count": question_count
        }
        result.append(CategoryResponse(**category_dict))
    
    return result

@router.get("/categories/tree", response_model=List[CategoryTreeResponse])
async def get_categories_tree(
    organization_id: Optional[int] = Query(None, description="组织ID，为空表示获取全局分类树"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取分类树结构"""
    # 如果指定了组织ID，检查权限
    if organization_id and not has_organization_access(db, current_user.id, organization_id):
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    def build_tree(categories, parent_id=None):
        """递归构建分类树"""
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                children = build_tree(categories, category.id)
                question_count = get_category_question_count(db, category.id)
                
                tree.append(CategoryTreeResponse(
                    id=category.id,
                    name=category.name,
                    description=category.description,
                    level=category.level,
                    path=category.path,
                    sort_order=category.sort_order,
                    is_active=category.is_active,
                    question_count=question_count,
                    children=children
                ))
        return sorted(tree, key=lambda x: x.sort_order)
    
    # 获取所有分类
    all_categories = get_categories(db, organization_id, skip=0, limit=1000)
    return build_tree(all_categories)

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category_detail(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取分类详情"""
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查权限
    if category.organization_id and not has_organization_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 获取子分类
    children = get_category_children(db, category_id)
    children_data = []
    for child in children:
        question_count = get_category_question_count(db, child.id)
        children_data.append(CategoryResponse(
            id=child.id,
            name=child.name,
            description=child.description,
            code=child.code,
            parent_id=child.parent_id,
            sort_order=child.sort_order,
            is_active=child.is_active,
            level=child.level,
            path=child.path,
            organization_id=child.organization_id,
            created_by=child.created_by,
            created_at=child.created_at,
            updated_at=child.updated_at,
            children=[],
            question_count=question_count
        ))
    
    # 获取题目数量
    question_count = get_category_question_count(db, category_id)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        code=category.code,
        parent_id=category.parent_id,
        sort_order=category.sort_order,
        is_active=category.is_active,
        level=category.level,
        path=category.path,
        organization_id=category.organization_id,
        created_by=category.created_by,
        created_at=category.created_at,
        updated_at=category.updated_at,
        children=children_data,
        question_count=question_count
    )

@router.post("/categories", response_model=CategoryResponse)
async def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新分类"""
    # 检查权限
    if category.organization_id and not has_organization_manage_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有管理权限")
    
    # 检查父分类是否存在
    if category.parent_id:
        parent = get_category(db, category.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
        
        # 检查父分类是否属于同一组织
        if parent.organization_id != category.organization_id:
            raise HTTPException(status_code=400, detail="父分类与当前分类不属于同一组织")
    
    try:
        db_category = create_category(db, category, current_user.id)
        
        return CategoryResponse(
            id=db_category.id,
            name=db_category.name,
            description=db_category.description,
            code=db_category.code,
            parent_id=db_category.parent_id,
            sort_order=db_category.sort_order,
            is_active=db_category.is_active,
            level=db_category.level,
            path=db_category.path,
            organization_id=db_category.organization_id,
            created_by=db_category.created_by,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at,
            children=[],
            question_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category_info(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新分类信息"""
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查权限
    if category.organization_id and not has_organization_manage_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有管理权限")
    
    # 检查父分类是否存在
    if category_update.parent_id:
        parent = get_category(db, category_update.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
        
        # 检查父分类是否属于同一组织
        if parent.organization_id != category.organization_id:
            raise HTTPException(status_code=400, detail="父分类与当前分类不属于同一组织")
        
        # 检查是否形成循环引用
        if category_update.parent_id == category_id:
            raise HTTPException(status_code=400, detail="不能将自己设为父分类")
    
    try:
        updated_category = update_category(db, category_id, category_update)
        if not updated_category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        question_count = get_category_question_count(db, category_id)
        
        return CategoryResponse(
            id=updated_category.id,
            name=updated_category.name,
            description=updated_category.description,
            code=updated_category.code,
            parent_id=updated_category.parent_id,
            sort_order=updated_category.sort_order,
            is_active=updated_category.is_active,
            level=updated_category.level,
            path=updated_category.path,
            organization_id=updated_category.organization_id,
            created_by=updated_category.created_by,
            created_at=updated_category.created_at,
            updated_at=updated_category.updated_at,
            children=[],
            question_count=question_count
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/categories/{category_id}")
async def delete_category_by_id(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除分类"""
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查权限
    if category.organization_id and not has_organization_manage_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有管理权限")
    
    try:
        deleted_category = delete_category(db, category_id)
        if not deleted_category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        return {"message": "分类删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.post("/categories/{category_id}/move")
async def move_category_to_parent(
    category_id: int,
    move_request: CategoryMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """移动分类到新的父分类下"""
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查权限
    if category.organization_id and not has_organization_manage_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有管理权限")
    
    # 检查目标父分类是否存在
    if move_request.target_parent_id:
        target_parent = get_category(db, move_request.target_parent_id)
        if not target_parent:
            raise HTTPException(status_code=404, detail="目标父分类不存在")
        
        # 检查目标父分类是否属于同一组织
        if target_parent.organization_id != category.organization_id:
            raise HTTPException(status_code=400, detail="目标父分类与当前分类不属于同一组织")
    
    try:
        moved_category = move_category(db, category_id, move_request.target_parent_id, move_request.position)
        if not moved_category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        return {"message": "分类移动成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories/{category_id}/children", response_model=List[CategoryResponse])
async def get_category_children_list(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取分类的子分类列表"""
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查权限
    if category.organization_id and not has_organization_access(db, current_user.id, category.organization_id):
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    children = get_category_children(db, category_id)
    
    result = []
    for child in children:
        question_count = get_category_question_count(db, child.id)
        result.append(CategoryResponse(
            id=child.id,
            name=child.name,
            description=child.description,
            code=child.code,
            parent_id=child.parent_id,
            sort_order=child.sort_order,
            is_active=child.is_active,
            level=child.level,
            path=child.path,
            organization_id=child.organization_id,
            created_by=child.created_by,
            created_at=child.created_at,
            updated_at=child.updated_at,
            children=[],
            question_count=question_count
        ))
    
    return result
