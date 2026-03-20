"""
问卷API集成测试
"""
import pytest
from datetime import datetime


class TestSurveyAPI:
    """问卷API测试"""

    def test_create_survey_success(self, client, auth_headers, sample_survey_data):
        """测试成功创建问卷"""
        response = client.post(
            "/api/v1/surveys/",
            headers=auth_headers,
            json=sample_survey_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_survey_data["title"]
        assert data["status"] == "draft"

    def test_create_survey_unauthorized(self, client, sample_survey_data):
        """测试未认证创建问卷"""
        response = client.post(
            "/api/v1/surveys/",
            json=sample_survey_data
        )
        assert response.status_code == 401

    def test_create_survey_missing_title(self, client, auth_headers):
        """测试创建问卷缺少标题"""
        response = client.post(
            "/api/v1/surveys/",
            headers=auth_headers,
            json={
                "description": "测试描述"
            }
        )
        assert response.status_code == 422

    def test_get_surveys_list(self, client, auth_headers, test_survey):
        """测试获取问卷列表"""
        response = client.get(
            "/api/v1/surveys/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_surveys_public(self, client):
        """测试公开获取问卷列表"""
        response = client.get("/api/v1/surveys/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_survey_by_id(self, client, test_survey):
        """测试通过ID获取问卷"""
        response = client.get(f"/api/v1/surveys/{test_survey.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_survey.id
        assert data["title"] == test_survey.title

    def test_get_survey_not_found(self, client):
        """测试获取不存在的问卷"""
        response = client.get("/api/v1/surveys/99999")
        assert response.status_code == 404

    def test_update_survey(self, client, auth_headers, test_survey):
        """测试更新问卷"""
        update_data = {
            "title": "更新的标题",
            "description": "更新的描述"
        }
        response = client.put(
            f"/api/v1/surveys/{test_survey.id}",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新的标题"
        assert data["description"] == "更新的描述"

    def test_update_survey_unauthorized(self, client, test_survey):
        """测试未认证更新问卷"""
        response = client.put(
            f"/api/v1/surveys/{test_survey.id}",
            json={"title": "更新"}
        )
        assert response.status_code == 401

    def test_update_survey_not_owner(self, client, auth_headers, db_session):
        """测试非所有者更新问卷"""
        # 创建另一个用户的问卷
        from backend.app.models import User, Survey
        other_user = User(
            username="other",
            email="other@example.com",
            hashed_password="hash"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_survey = Survey(
            title="其他问卷",
            created_by_user_id=other_user.id
        )
        db_session.add(other_survey)
        db_session.commit()
        
        # 尝试更新不属于自己的问卷
        response = client.put(
            f"/api/v1/surveys/{other_survey.id}",
            headers=auth_headers,
            json={"title": "尝试更新"}
        )
        # 根据实际权限实现，可能返回403或404
        assert response.status_code in [403, 404]

    def test_delete_survey(self, client, auth_headers, db_session):
        """测试删除问卷"""
        # 创建临时问卷
        from backend.app.models import Survey
        temp_survey = Survey(
            title="临时问卷",
            created_by_user_id=1  # 假设auth_headers对应的用户ID是1
        )
        db_session.add(temp_survey)
        db_session.commit()
        db_session.refresh(temp_survey)
        
        response = client.delete(
            f"/api/v1/surveys/{temp_survey.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_survey_unauthorized(self, client, db_session):
        """测试未认证删除问卷"""
        from backend.app.models import Survey
        temp_survey = Survey(
            title="临时问卷",
            created_by_user_id=1
        )
        db_session.add(temp_survey)
        db_session.commit()
        
        response = client.delete(f"/api/v1/surveys/{temp_survey.id}")
        assert response.status_code == 401

    def test_add_question_to_survey(self, client, auth_headers, test_survey, test_question):
        """测试添加题目到问卷"""
        response = client.post(
            f"/api/v1/surveys/{test_survey.id}/questions/",
            headers=auth_headers,
            json={
                "question_id": test_question.id,
                "order": 1
            }
        )
        assert response.status_code in [200, 201]

    def test_get_survey_questions(self, client, test_survey):
        """测试获取问卷题目列表"""
        response = client.get(f"/api/v1/surveys/{test_survey.id}/questions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_publish_survey(self, client, auth_headers, test_survey):
        """测试发布问卷"""
        response = client.put(
            f"/api/v1/surveys/{test_survey.id}/publish",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_close_survey(self, client, auth_headers, test_survey):
        """测试关闭问卷"""
        # 先发布问卷
        client.put(
            f"/api/v1/surveys/{test_survey.id}/publish",
            headers=auth_headers
        )
        
        # 再关闭问卷
        response = client.put(
            f"/api/v1/surveys/{test_survey.id}/close",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"

    def test_duplicate_survey(self, client, auth_headers, test_survey):
        """测试复制问卷"""
        response = client.post(
            f"/api/v1/surveys/{test_survey.id}/duplicate",
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"].startswith("副本")
