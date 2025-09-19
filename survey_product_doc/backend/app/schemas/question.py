# backend/app/schemas/question.py
"""
问题数据模型Schema模块
定义问题相关的Pydantic模型，用于数据验证、序列化和反序列化
支持问卷内问题和全局题库问题两种模式
"""

# ===== 导入依赖 =====
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any
from datetime import datetime
from backend.app.models.question import QuestionType

# ===== 基础问题模型 =====

class QuestionBase(BaseModel):
    """
    问题基础模型
    定义问题的基本字段和验证规则
    """
    text: str = Field(..., min_length=1, description="问题文本")
    type: QuestionType = Field(..., description="问题类型")
    is_required: bool = Field(False, description="是否必填")
    order: int = Field(0, description="问题在问卷中的排序")
    options: Optional[List[str]] = Field(None, description="选择题的选项列表")

    @validator('options', pre=True, always=True)
    def validate_options_for_type(cls, v, values):
        """
        验证选项字段与问题类型的匹配性
        
        Args:
            v: 选项值
            values: 其他字段的值
            
        Returns:
            验证后的选项值
            
        Raises:
            ValueError: 当选项与问题类型不匹配时
        """
        q_type = values.get('type')
        if q_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
            # 选择题类型必须提供选项
            if not v:
                raise ValueError("选择题类型必须提供选项")
            if not isinstance(v, list) or not all(isinstance(item, str) for item in v):
                raise ValueError("选项必须是字符串列表")
        elif v is not None and q_type in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
            # 文本或数字输入类型不能有选项
            raise ValueError("文本或数字输入类型的问题不能有选项")
        return v

# ===== 问题创建模型 =====

class QuestionCreate(QuestionBase):
    """
    问题创建模型
    用于创建新问题时的数据验证
    
    注意：survey_id不在这里定义，因为会在API路径或依赖中获取
    """
    pass

# ===== 问题更新模型 =====

class QuestionUpdate(QuestionBase):
    """
    问题更新模型
    用于更新现有问题时的数据验证
    所有字段都是可选的，支持部分更新
    """
    text: Optional[str] = Field(None, min_length=1, description="问题文本")
    type: Optional[QuestionType] = Field(None, description="问题类型")
    is_required: Optional[bool] = Field(None, description="是否必填")
    order: Optional[int] = Field(None, description="问题在问卷中的排序")
    options: Optional[List[str]] = Field(None, description="选择题的选项列表")

    @validator('options', pre=True, always=True)
    def validate_options_for_update(cls, v, values):
        """
        验证更新时的选项字段与问题类型的匹配性
        
        Args:
            v: 选项值
            values: 其他字段的值
            
        Returns:
            验证后的选项值
            
        Raises:
            ValueError: 当选项与问题类型不匹配时
        """
        # 在更新时，如果类型没有改变，或者改变为选择题，才需要验证选项
        if 'type' in values and values['type'] in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
            # 选择题类型必须提供选项
            if not v:
                raise ValueError("选择题类型必须提供选项")
            if not isinstance(v, list) or not all(isinstance(item, str) for item in v):
                raise ValueError("选项必须是字符串列表")
        elif 'type' in values and v is not None and values['type'] in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
            # 文本或数字输入类型不能有选项
            raise ValueError("文本或数字输入类型的问题不能有选项")
        return v

# ===== 问题响应模型 =====

class QuestionResponse(QuestionBase):
    """
    问题响应模型
    用于API响应时的数据序列化
    包含数据库生成的ID和关联的survey_id
    """
    id: int
    survey_id: Optional[int] = None
    owner_id: Optional[int] = None  # 添加创建者ID字段
    owner_name: Optional[str] = None  # 添加创建者用户名字段
    usage_count: Optional[int] = 0  # 添加使用次数字段
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间

    class Config:
        """
        Pydantic配置类
        定义模型的行为和序列化规则
        """
        from_attributes = True  # 允许从SQLAlchemy模型直接创建Pydantic模型
        use_enum_values = True  # 将枚举值转换为字符串

# ===== 分页响应模型 =====

class QuestionListResponse(BaseModel):
    """
    题目列表分页响应模型
    用于返回分页的题目列表和总数
    """
    items: List[QuestionResponse]
    total: int
    skip: int
    limit: int
    page: int
    pages: int

    class Config:
        """
        Pydantic配置类
        """
        from_attributes = True
