"""
问卷模型单元测试
"""
import pytest
from datetime import datetime
from backend.app.models import Survey


class TestSurveyModel:
    """问卷模型测试"""

    def test_create_survey_success(self):
        """测试成功创建问卷"""
        survey = Survey(
            title="测试问卷",
            description="这是一个测试问卷",
            created_by_user_id=1,
            status="draft"
        )
        assert survey.title == "测试问卷"
        assert survey.description == "这是一个测试问卷"
        assert survey.created_by_user_id == 1
        assert survey.status == "draft"

    def test_survey_default_status(self):
        """测试问卷默认状态"""
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1
        )
        assert survey.status == "draft"

    def test_survey_status_transitions(self):
        """测试问卷状态转换"""
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1,
            status="draft"
        )
        
        # 草稿 -> 进行中
        survey.status = "active"
        assert survey.status == "active"
        
        # 进行中 -> 已关闭
        survey.status = "closed"
        assert survey.status == "closed"

    def test_survey_time_validation(self):
        """测试问卷时间验证"""
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1,
            start_time=datetime(2026, 1, 1, 0, 0, 0),
            end_time=datetime(2026, 12, 31, 23, 59, 59)
        )
        assert survey.start_time < survey.end_time

    def test_survey_organization_relationship(self, db_session):
        """测试问卷组织关系"""
        from backend.app.models import Organization, User
        
        org = Organization(
            name="测试组织",
            description="测试",
            owner_id=1
        )
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pass"
        )
        
        survey = Survey(
            title="测试问卷",
            created_by_user_id=user.id,
            organization_id=org.id
        )
        
        db_session.add(org)
        db_session.add(user)
        db_session.add(survey)
        db_session.commit()
        
        assert survey.organization_id == org.id

    def test_survey_title_required(self):
        """测试问卷标题必填"""
        with pytest.raises(Exception):
            survey = Survey(
                created_by_user_id=1
            )
            # SQLAlchemy会在数据库层面强制检查

    def test_survey_description_optional(self):
        """测试问卷描述可选"""
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1
        )
        assert survey.description is None

    def test_survey_with_questions(self, db_session):
        """测试问卷题目关系"""
        from backend.app.models import Question, SurveyQuestion
        
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1
        )
        
        question1 = Question(
            text="问题1",
            type="single_choice",
            owner_id=1
        )
        question2 = Question(
            text="问题2",
            type="text_input",
            owner_id=1
        )
        
        survey_question1 = SurveyQuestion(
            survey_id=survey.id,
            question_id=question1.id,
            order=1
        )
        survey_question2 = SurveyQuestion(
            survey_id=survey.id,
            question_id=question2.id,
            order=2
        )
        
        db_session.add(survey)
        db_session.add(question1)
        db_session.add(question2)
        db_session.add(survey_question1)
        db_session.add(survey_question2)
        db_session.commit()
        
        assert len(survey.questions) == 2

    def test_survey_cascade_delete(self, db_session):
        """测试问卷级联删除"""
        from backend.app.models import Question, SurveyQuestion, SurveyAnswer
        
        survey = Survey(
            title="测试问卷",
            created_by_user_id=1
        )
        
        question = Question(
            text="问题1",
            type="single_choice",
            owner_id=1
        )
        
        survey_question = SurveyQuestion(
            survey_id=survey.id,
            question_id=question.id,
            order=1
        )
        
        survey_answer = SurveyAnswer(
            survey_id=survey.id,
            question_id=question.id,
            answer_text="答案"
        )
        
        db_session.add(survey)
        db_session.add(question)
        db_session.add(survey_question)
        db_session.add(survey_answer)
        db_session.commit()
        
        # 删除问卷应该级联删除关联数据
        db_session.delete(survey)
        db_session.commit()
        
        # 验证关联数据也被删除
        assert db_session.query(SurveyAnswer).filter_by(survey_id=survey.id).first() is None
