# backend/app/schemas/__init__.py

from .user import UserCreate, UserLogin, UserResponse, UserUpdate, OrganizationResponse
from .token import Token
from backend.app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyResponse
from backend.app.schemas.user import UserCreate, UserUpdate
from .question import QuestionCreate, QuestionBase
from .answer import SurveyAnswer, SurveyAnswerCreate, SurveyAnswerResponse, SurveyAnswerInDBBase
from .organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from .organization_member import OrganizationMemberCreate, OrganizationMemberUpdate, OrganizationMemberResponse
from .department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from .participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from .category import CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse, CategoryMoveRequest, CategoryBulkUpdateRequest
from .msg import Msg

# 方便其他模块通过 schemas.User 等方式引用
__all__ = [
    "UserCreate", "UserUpdate", "UserResponse",
    "SurveyCreate", "SurveyUpdate", "SurveyResponse",
    "QuestionCreate", "QuestionBase",
    "SurveyAnswer", "SurveyAnswerCreate", "SurveyAnswerResponse", "SurveyAnswerInDBBase",
    "OrganizationCreate", "OrganizationUpdate", "OrganizationResponse",
    "OrganizationMemberCreate", "OrganizationMemberUpdate", "OrganizationMemberResponse",
    "DepartmentCreate", "DepartmentUpdate", "DepartmentResponse",
    "ParticipantCreate", "ParticipantUpdate", "ParticipantResponse",
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse", "CategoryTreeResponse", "CategoryMoveRequest", "CategoryBulkUpdateRequest"
]
