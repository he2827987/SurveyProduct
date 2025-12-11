# backend/app/models/question.py
"""
问题数据库模型模块
定义问题相关的SQLAlchemy ORM模型，包括问题类型枚举和问题表结构
支持问卷内问题和全局题库问题两种模式
"""

# ===== 导入依赖 =====
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base
from typing import Optional, cast
import enum
import datetime



# ===== 问题类型枚举 =====

class QuestionType(enum.Enum):
    """
    问题类型枚举
    定义系统支持的所有问题类型
    """
    SINGLE_CHOICE = "single_choice"  # 单选题
    MULTI_CHOICE = "multi_choice"    # 多选题
    TEXT_INPUT = "text_input"        # 文本输入题（填空）
    NUMBER_INPUT = "number_input"    # 数字输入题

# ===== 问题数据库模型 =====

class Question(Base):
    """
    问题数据库模型
    定义问题表的结构和关系映射
    支持问卷内问题和全局题库问题两种模式
    """
    __tablename__ = "questions"

    # ===== 基础字段 =====
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)  # 问题文本内容
    type = Column(Enum(QuestionType), nullable=False)  # 问题类型

    # ===== 关联字段 =====
    # 问卷关联（通过中间表实现）
    survey_questions = relationship("SurveyQuestion", back_populates="question")

    # 所有者关联（可为空，表示系统默认问题）
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="questions")
    
    # 组织关联（可为空，表示全局题库问题）
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="questions")
    
    # 分类关联（可为空，表示未分类）
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")
    
    # 标签关联（多对多关系）
    tags = relationship("Tag", secondary="question_tags", back_populates="questions")

    # ===== 问题属性字段 =====
    # 选项字段：存储JSON格式的选项列表，如'[{"text": "选项A", "score": 5}, {"text": "选项B", "score": 3}]'
    # 暂时使用Text字段存储JSON字符串，如果选项复杂可考虑单独的表
    options: Optional[str] = cast(Optional[str], Column(Text, nullable=True))
    
    # 分值范围设置
    min_score = Column(Integer, default=0, nullable=True)  # 选项分值最小值
    max_score = Column(Integer, default=10, nullable=True)  # 选项分值最大值
    
    is_required = Column(Boolean, default=False)  # 是否必填
    order = Column(Integer, default=0)  # 问题在问卷中的排序
    usage_count = Column(Integer, default=0)  # 使用次数统计
    
    # ===== 时间戳字段 =====
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    # ===== 反向关系 =====
    # 回答关系（已注释，避免循环依赖）
    # answers = relationship("SurveyAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        """
        模型的字符串表示
        
        Returns:
            str: 问题的字符串表示
        """
        return f"<Question(id={self.id}, text='{self.text}', type='{self.type.value}')>"
