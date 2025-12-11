# backend/app/models/__init__.py

from .user import User
from .survey import Survey
from .question import Question
from .answer import SurveyAnswer
from .organization import Organization
from .organization_member import OrganizationMember
from .department import Department
from .participant import Participant
from .category import Category
from .survey_question import SurveyQuestion
from .tag import Tag

# 你也可以在这里定义一个列表，包含所有模型类，方便 Base.metadata.create_all 找到它们
# 但由于 main.py 中已经导入了整个 models 包，SQLAlchemy 会自动发现继承自 Base 的类
# 所以这里不强制要求，但为了清晰性，可以保留。
__all__ = ["User", "Survey", "Question", "SurveyAnswer", "Organization", "OrganizationMember", "Department", "Participant", "Category", "SurveyQuestion", "Tag"]
