# backend/app/api/tag_api.py
"""
标签管理API模块
提供标签的CRUD操作和查询功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json

from backend.app.database import get_db
from backend.app.models.tag import Tag, question_tags
from backend.app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter(prefix="/question-tags", tags=["Question Tags"])

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    try:
        # 查询标签并统计每个标签关联的题目数量
        tags_with_count = db.query(
            Tag,
            func.count(question_tags.c.question_id).label('question_count')
        ).outerjoin(question_tags).group_by(Tag.id).offset(skip).limit(limit).all()
        
        result = []
        for tag, count in tags_with_count:
            result.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "question_count": count
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取标签列表失败: {str(e)}")

@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    """创建新标签"""
    try:
        # 检查标签名称是否已存在
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(status_code=400, detail="标签名称已存在")
        
        # 创建新标签
        new_tag = Tag(
            name=tag_data.name,
            color=tag_data.color or "#409EFF",
            description=tag_data.description
        )
        
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        
        return {
            "id": new_tag.id,
            "name": new_tag.name,
            "color": new_tag.color,
            "description": new_tag.description,
            "question_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建标签失败: {str(e)}")

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db)
):
    """更新标签"""
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")
        
        # 检查名称是否与其他标签重复
        if tag_data.name and tag_data.name != tag.name:
            existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
            if existing_tag:
                raise HTTPException(status_code=400, detail="标签名称已存在")
        
        # 更新标签
        if tag_data.name:
            tag.name = tag_data.name
        if tag_data.color:
            tag.color = tag_data.color
        if tag_data.description is not None:
            tag.description = tag_data.description
        
        db.commit()
        db.refresh(tag)
        
        # 获取题目数量
        question_count = db.query(func.count(question_tags.c.question_id)).filter(
            question_tags.c.tag_id == tag.id
        ).scalar()
        
        return {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "description": tag.description,
            "question_count": question_count
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新标签失败: {str(e)}")

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """删除标签"""
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")
        
        # 检查是否有题目使用此标签
        question_count = db.query(func.count(question_tags.c.question_id)).filter(
            question_tags.c.tag_id == tag.id
        ).scalar()
        
        if question_count > 0:
            raise HTTPException(status_code=400, detail=f"标签正在被 {question_count} 个题目使用，无法删除")
        
        db.delete(tag)
        db.commit()
        
        return {"message": "标签删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除标签失败: {str(e)}")
