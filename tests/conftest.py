"""
测试配置文件
包含所有共享的pytest fixtures
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import Mock, patch

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.database import Base, get_db
from backend.app.models import User, Organization, Survey, Question, SurveyQuestion, SurveyAnswer
from backend.app.services.user_service import get_password_hash


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    # 使用内存SQLite数据库进行测试
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """创建测试数据库会话"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    from backend.app.main import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role="researcher",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session) -> User:
    """创建测试管理员"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_organization(db_session: Session, test_admin: User) -> Organization:
    """创建测试组织"""
    org = Organization(
        name="测试组织",
        description="这是一个测试组织",
        owner_id=test_admin.id
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_survey(db_session: Session, test_user: User, test_organization: Organization) -> Survey:
    """创建测试问卷"""
    survey = Survey(
        title="测试问卷",
        description="这是一个测试问卷",
        created_by_user_id=test_user.id,
        organization_id=test_organization.id,
        status="draft"
    )
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    return survey


@pytest.fixture
def test_question(db_session: Session, test_user: User) -> Question:
    """创建测试题目"""
    question = Question(
        text="这是一个测试题目吗？",
        type="single_choice",
        options='["选项A", "选项B", "选项C"]',
        is_required=True,
        order=1,
        owner_id=test_user.id,
        min_score=0,
        max_score=10
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question


@pytest.fixture
def auth_headers(client, test_admin: User) -> dict:
    """获取认证头"""
    response = client.post(
        "/api/v1/users/login/access-token",
        data={
            "username": test_admin.username,
            "password": "admin123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_llm_response():
    """Mock LLM API响应"""
    return Mock(return_value={
        "summary": "这是一个测试总结",
        "insights": ["洞察1", "洞察2"],
        "recommendations": ["建议1", "建议2"]
    })


@pytest.fixture
def temp_file():
    """创建临时文件"""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def sample_survey_data():
    """示例问卷数据"""
    return {
        "title": "员工满意度调查",
        "description": "调查员工对公司的满意度",
        "status": "draft",
        "start_time": "2026-01-01T00:00:00",
        "end_time": "2026-12-31T23:59:59"
    }


@pytest.fixture
def sample_question_data():
    """示例题目数据"""
    return {
        "text": "您对当前的工作环境满意吗？",
        "type": "single_choice",
        "options": ["非常满意", "满意", "一般", "不满意", "非常不满意"],
        "is_required": True,
        "min_score": 1,
        "max_score": 5
    }


@pytest.fixture
def sample_answer_data(test_survey: Survey, test_question: Question):
    """示例答案数据"""
    return {
        "survey_id": test_survey.id,
        "question_id": test_question.id,
        "answer_text": "非常满意",
        "score": 5
    }


# 测试数据清理fixture
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session: Session):
    """自动清理测试数据"""
    yield
    # 测试完成后清理数据
    db_session.query(SurveyAnswer).delete()
    db_session.query(SurveyQuestion).delete()
    db_session.query(Question).delete()
    db_session.query(Survey).delete()
    db_session.query(Organization).delete()
    db_session.query(User).delete()
    db_session.commit()
