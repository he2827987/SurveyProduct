# backend/app/schemas/question.py
"""
问题数据模型Schema模块
定义问题相关的Pydantic模型，用于数据验证、序列化和反序列化
支持问卷内问题和全局题库问题两种模式
"""

# ===== 导入依赖 =====
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Union
from datetime import datetime
from backend.app.models.question import QuestionType
import json

# ===== 选项模型 =====

class QuestionOption(BaseModel):
    """
    问题选项模型
    """
    text: str = Field(..., description="选项文本")
    score: Optional[int] = Field(None, description="选项分值")
    is_correct: Optional[bool] = Field(False, description="正确选项")

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
    category_id: Optional[int] = Field(None, description="分类ID")
    options: Optional[List[Union[QuestionOption, str]]] = Field(None, description="选择题的选项列表")
    min_score: Optional[int] = Field(0, description="选项分值最小值")
    max_score: Optional[int] = Field(10, description="选项分值最大值")
    tags: Optional[List[str]] = Field(None, description="题目标签列表")
    parent_question_id: Optional[int] = Field(None, description="关联题的父题目ID")
    trigger_options: Optional[List[Dict[str, Any]]] = Field(None, description="触发条件列表，格式：[{\"option_text\": \"选项A\"}]")

    @validator('options', pre=True, always=True)
    def validate_options_for_type(cls, v, values):
        """
        验证选项字段与问题类型的匹配性
        """
        # 如果是字符串（从数据库读取时），尝试解析为JSON
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass

        q_type = values.get('type')
        # 关联题可以是任何类型，所以先检查是否是关联题
        is_conditional = values.get('parent_question_id') is not None
        
        if q_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE, QuestionType.SORT_ORDER]:
            # 选择题类型和排序题必须提供选项（包括关联题中的选择题和排序题）
            if not v:
                raise ValueError("选择题类型和排序题必须提供选项")
            if not isinstance(v, list):
                raise ValueError("选项必须是列表")
            
            # 排序题至少需要2个选项
            if q_type == QuestionType.SORT_ORDER and len(v) < 2:
                raise ValueError("排序题至少需要2个选项")
            
            # 验证列表项
            for item in v:
                if isinstance(item, str):
                    continue
                if isinstance(item, dict) or isinstance(item, QuestionOption):
                    continue
                raise ValueError("选项必须是字符串或包含text, score, is_correct的对象")
                
        elif v is not None and q_type in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
            # 文本、数字输入类型不能有选项
            # 注意：如果是空列表，也可以接受
            if isinstance(v, list) and len(v) > 0:
                raise ValueError("文本、数字输入类型的问题不能有选项")
        return v
    
    @validator('parent_question_id', 'trigger_options')
    def validate_conditional_question(cls, v, values, field):
        """
        验证关联题的父题目和触发条件
        关联题可以是任何题目类型，只要设置了parent_question_id和trigger_options
        """
        # 如果设置了parent_question_id，则必须同时设置trigger_options
        parent_id = values.get('parent_question_id') if field.name == 'trigger_options' else v
        trigger_opts = v if field.name == 'trigger_options' else values.get('trigger_options')
        
        if field.name == 'parent_question_id':
            # 如果设置了parent_question_id，必须同时设置trigger_options
            if v is not None:
                if not trigger_opts or not isinstance(trigger_opts, list) or len(trigger_opts) == 0:
                    raise ValueError("设置父题目ID时，必须同时指定至少一个触发选项")
        elif field.name == 'trigger_options':
            # 如果设置了trigger_options，必须同时设置parent_question_id
            if v is not None:
                if not parent_id:
                    raise ValueError("设置触发选项时，必须同时指定父题目ID")
                if not isinstance(v, list) or len(v) == 0:
                    raise ValueError("关联题必须指定至少一个触发选项")
                for trigger in v:
                    if not isinstance(trigger, dict) or 'option_text' not in trigger:
                        raise ValueError("触发条件格式错误，应为[{\"option_text\": \"选项A\"}]")
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
    options: Optional[List[Union[QuestionOption, str]]] = Field(None, description="选择题的选项列表")
    min_score: Optional[int] = Field(None, description="选项分值最小值")
    max_score: Optional[int] = Field(None, description="选项分值最大值")

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
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass

        # 在更新时，如果类型没有改变，或者改变为选择题，才需要验证选项
        if 'type' in values and values['type'] in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
            # 选择题类型必须提供选项
            if not v:
                raise ValueError("选择题类型必须提供选项")
            if not isinstance(v, list):
                raise ValueError("选项必须是列表")
            
            for item in v:
                if isinstance(item, str):
                    continue
                if isinstance(item, dict) or isinstance(item, QuestionOption):
                    continue
                raise ValueError("选项必须是字符串或包含text, score, is_correct的对象")

        elif 'type' in values and v is not None and values['type'] in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
            # 文本或数字输入类型不能有选项
            if isinstance(v, list) and len(v) > 0:
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

    @validator('tags', pre=True, always=True)
    def extract_tag_names(cls, v):
        """
        从 Tag 对象列表中提取标签名称
        如果 v 是 Tag 对象列表，返回 [tag.name]
        如果 v 是字符串列表，直接返回
        """
        if not v:
            return []
        
        # 处理 ORM 对象列表
        if isinstance(v, list):
            # 检查列表中的第一个元素，如果是 Tag 对象（具有 name 属性），则提取 name
            # 我们通过检查属性是否存在来判断
            return [
                item.name if hasattr(item, 'name') else item 
                for item in v
            ]
            
        return v

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
