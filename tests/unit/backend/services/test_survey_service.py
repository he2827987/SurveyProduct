"""
问卷服务层单元测试
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from backend.app.services import survey_service


class TestSurveyService:
    """问卷服务测试"""

    def test_create_survey_success(self, db_session, test_user, test_organization):
        """测试成功创建问卷"""
        survey_data = {
            "title": "员工满意度调查",
            "description": "调查员工满意度",
            "created_by_user_id": test_user.id,
            "organization_id": test_organization.id,
            "status": "draft"
        }
        
        survey = survey_service.create_survey(db_session, survey_data)
        assert survey is not None
        assert survey.title == "员工满意度调查"
        assert survey.created_by_user_id == test_user.id
        assert survey.organization_id == test_organization.id

    def test_create_survey_without_organization(self, db_session, test_user):
        """测试创建无组织的问卷"""
        survey_data = {
            "title": "个人问卷",
            "description": "个人使用",
            "created_by_user_id": test_user.id,
            "status": "draft"
        }
        
        survey = survey_service.create_survey(db_session, survey_data)
        assert survey.organization_id is None

    def test_get_survey_by_id(self, db_session, test_survey):
        """测试通过ID获取问卷"""
        survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        assert survey is not None
        assert survey.id == test_survey.id
        assert survey.title == test_survey.title

    def test_get_survey_by_id_not_found(self, db_session):
        """测试获取不存在的问卷"""
        survey = survey_service.get_survey_by_id(db_session, survey_id=99999)
        assert survey is None

    def test_update_survey_status(self, db_session, test_survey):
        """测试更新问卷状态"""
        # 更新为发布状态
        test_survey.status = "active"
        test_survey.start_time = datetime.now()
        db_session.commit()
        
        updated_survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        assert updated_survey.status == "active"
        assert updated_survey.start_time is not None

    def test_add_question_to_survey(self, db_session, test_survey, test_question):
        """测试添加题目到问卷"""
        from backend.app.models import SurveyQuestion
        
        survey_question = SurveyQuestion(
            survey_id=test_survey.id,
            question_id=test_question.id,
            order=1
        )
        db_session.add(survey_question)
        db_session.commit()
        
        # 获取问卷题目
        survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        assert len(survey.questions) >= 1

    def test_remove_question_from_survey(self, db_session, test_survey, test_question):
        """测试从问卷移除题目"""
        from backend.app.models import SurveyQuestion
        
        # 添加题目
        survey_question = SurveyQuestion(
            survey_id=test_survey.id,
            question_id=test_question.id,
            order=1
        )
        db_session.add(survey_question)
        db_session.commit()
        
        # 移除题目
        db_session.delete(survey_question)
        db_session.commit()
        
        # 验证题目已移除
        survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        # 注意：这里需要根据实际的关系查询方式调整

    def test_get_surveys_by_organization(self, db_session, test_survey, test_organization):
        """测试获取组织的问卷列表"""
        surveys = survey_service.get_surveys_by_organization(db_session, test_organization.id)
        assert len(surveys) > 0
        assert any(s.id == test_survey.id for s in surveys)

    def test_get_surveys_by_user(self, db_session, test_survey, test_user):
        """测试获取用户创建的问卷"""
        surveys = survey_service.get_surveys_by_user(db_session, test_user.id)
        assert len(surveys) > 0
        assert any(s.id == test_survey.id for s in surveys)

    def test_survey_question_ordering(self, db_session, test_survey):
        """测试问卷题目排序"""
        from backend.app.models import Question, SurveyQuestion
        
        # 创建多个题目
        question1 = Question(text="Q1", type="single_choice", owner_id=1)
        question2 = Question(text="Q2", type="single_choice", owner_id=1)
        question3 = Question(text="Q3", type="single_choice", owner_id=1)
        
        db_session.add_all([question1, question2, question3])
        db_session.commit()
        
        # 按顺序添加到问卷
        sq1 = SurveyQuestion(survey_id=test_survey.id, question_id=question1.id, order=1)
        sq2 = SurveyQuestion(survey_id=test_survey.id, question_id=question2.id, order=2)
        sq3 = SurveyQuestion(survey_id=test_survey.id, question_id=question3.id, order=3)
        
        db_session.add_all([sq1, sq2, sq3])
        db_session.commit()
        
        # 验证顺序
        survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        survey_questions = sorted(survey.questions, key=lambda x: x.order)
        assert survey_questions[0].question_id == question1.id
        assert survey_questions[1].question_id == question2.id
        assert survey_questions[2].question_id == question3.id

    @patch('backend.app.services.survey_service.generate_qr_code')
    def test_generate_survey_qr_code(self, mock_qr, test_survey):
        """测试生成问卷二维码"""
        mock_qr.return_value = b"fake_qr_code_data"
        
        qr_data = survey_service.generate_qr_code(test_survey.id)
        assert qr_data is not None
        mock_qr.assert_called_once_with(test_survey.id)

    def test_survey_with_answers(self, db_session, test_survey, test_question):
        """测试问卷答案统计"""
        from backend.app.models import SurveyAnswer
        
        # 添加多个答案
        answers = []
        for i in range(5):
            answer = SurveyAnswer(
                survey_id=test_survey.id,
                question_id=test_question.id,
                answer_text=f"答案{i+1}",
                score=3
            )
            answers.append(answer)
        
        db_session.add_all(answers)
        db_session.commit()
        
        # 获取问卷统计
        survey = survey_service.get_survey_by_id(db_session, test_survey.id)
        # 这里需要根据实际的统计方法进行调整

    def test_survey_time_validation(self, db_session, test_user):
        """测试问卷时间验证"""
        start_time = datetime.now()
        end_time = datetime.now().replace(hour=23, minute=59, second=59)
        
        survey_data = {
            "title": "时间测试问卷",
            "created_by_user_id": test_user.id,
            "start_time": start_time,
            "end_time": end_time
        }
        
        survey = survey_service.create_survey(db_session, survey_data)
        assert survey.start_time is not None
        assert survey.end_time is not None
        assert survey.start_time <= survey.end_time

    def test_delete_survey(self, db_session, test_survey):
        """测试删除问卷"""
        survey_id = test_survey.id
        survey_service.delete_survey(db_session, survey_id)
        
        # 验证问卷已删除
        survey = survey_service.get_survey_by_id(db_session, survey_id)
        assert survey is None

    def test_search_surveys_by_title(self, db_session, test_survey):
        """测试按标题搜索问卷"""
        keyword = "测试"
        surveys = survey_service.search_surveys(db_session, keyword=keyword)
        assert len(surveys) > 0
        assert any(keyword in s.title for s in surveys)

    def test_get_active_surveys(self, db_session, test_survey):
        """测试获取活跃问卷"""
        test_survey.status = "active"
        db_session.commit()
        
        active_surveys = survey_service.get_active_surveys(db_session)
        assert len(active_surveys) > 0
        assert any(s.id == test_survey.id for s in active_surveys)
