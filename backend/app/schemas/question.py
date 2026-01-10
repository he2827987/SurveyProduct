# backend/app/schemas/question.py
"""
问题数据模型Schema模块
定义问题相关的Pydantic模型，用于数据验证、序列化和反序列化
支持问卷内问题和全局题库问题两种模式
"""

# ===== 导入依赖 =====
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any, Union, Dict
from datetime import datetime
from backend.app.models.question import QuestionType
import json


def _prepare_values(values):
    if isinstance(values, dict):
        return values
    if hasattr(values, "__dict__"):
        result = {k: v for k, v in vars(values).items() if not k.startswith("_sa")}
        return result
    return values

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

    @model_validator(mode="before")
    def validate_options_for_type(cls, values):
        """
        验证选项字段与问题类型的匹配性
        """
        values = _prepare_values(values)
        options = values.get("options")
        # 如果是字符串（从数据库读取时），尝试解析为JSON
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except json.JSONDecodeError:
                pass
        values["options"] = options

        q_type = values.get("type")

        if q_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE, QuestionType.SORT_ORDER]:
            if not options:
                raise ValueError("选择题类型和排序题必须提供选项")
            if not isinstance(options, list):
                raise ValueError("选项必须是列表")

            if q_type == QuestionType.SORT_ORDER and len(options) < 2:
                raise ValueError("排序题至少需要2个选项")

            for item in options:
                if isinstance(item, str):
                    continue
                if isinstance(item, dict) or isinstance(item, QuestionOption):
                    continue
                raise ValueError("选项必须是字符串或包含text, score, is_correct的对象")
        elif options is not None and q_type in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
            if isinstance(options, list) and len(options) > 0:
                raise ValueError("文本、数字输入类型的问题不能有选项")

        return values
    
    @model_validator(mode="after")
    def validate_conditional_question(self):
        """
        验证关联题配置：父题目ID和触发选项必须同时存在或同时为空
        在mode="after"时，self已经是完整的模型实例
        """
        parent_id = self.parent_question_id
        trigger_opts = self.trigger_options

        # 只有当真正设置了父题目ID（不为None）时才验证触发选项
        if parent_id is not None:
            if not trigger_opts or not isinstance(trigger_opts, list) or len(trigger_opts) == 0:
                raise ValueError("设置父题目ID时，必须同时指定至少一个触发选项")
        
        # 只有当真正提供了触发选项（不为空）时才验证父题目ID
        # 空数组或None都视为未设置，不需要验证
        if trigger_opts and isinstance(trigger_opts, list) and len(trigger_opts) > 0:
            if not parent_id:
                raise ValueError("设置触发选项时，必须同时指定父题目ID")
            for trigger in trigger_opts:
                if not isinstance(trigger, dict) or "option_text" not in trigger:
                    raise ValueError("触发条件格式错误，应为[{\"option_text\": \"选项A\"}]")
        
        return self
    
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

    @model_validator(mode="before")
    def validate_options_for_update(cls, values):
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
        values = _prepare_values(values)
        options = values.get("options")
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except json.JSONDecodeError:
                pass
        values["options"] = options

        q_type = values.get("type")
        if q_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE]:
            if not options:
                raise ValueError("选择题类型必须提供选项")
            if not isinstance(options, list):
                raise ValueError("选项必须是列表")
            for item in options:
                if isinstance(item, str):
                    continue
                if isinstance(item, dict) or isinstance(item, QuestionOption):
                    continue
                raise ValueError("选项必须是字符串或包含text, score, is_correct的对象")
        elif q_type in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT] and options is not None:
            if isinstance(options, list) and len(options) > 0:
                raise ValueError("文本或数字输入类型的问题不能有选项")

        return values

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

    @model_validator(mode="after")
    def normalize_tags(cls, values):
        """
        Normalize tags to plain strings after validation.
        """
        if isinstance(values, dict):
            tags = values.get("tags")
        else:
            tags = getattr(values, "tags", None)

        normalized = []
        if tags:
            for item in tags:
                normalized.append(item.name if hasattr(item, "name") else item)

        if isinstance(values, dict):
            values["tags"] = normalized
            return values

        setattr(values, "tags", normalized)
        return values

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
