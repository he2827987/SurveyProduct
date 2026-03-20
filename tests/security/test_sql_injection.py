"""
安全测试 - SQL注入
"""
import pytest


class TestSQLInjection:
    """SQL注入测试"""

    def test_sql_injection_in_login_username(self, client):
        """测试登录接口SQL注入"""
        malicious_payloads = [
            "admin' OR '1'='1",
            "admin'--",
            "admin' /*",
            "admin' OR 1=1--",
            "' UNION SELECT NULL,NULL,NULL--"
        ]
        
        for payload in malicious_payloads:
            response = client.post(
                "/api/v1/users/login/access-token",
                data={
                    "username": payload,
                    "password": "anything"
                }
            )
            # 应该返回认证失败，而不是成功
            assert response.status_code in [401, 403, 422]

    def test_sql_injection_in_survey_id(self, client):
        """测试问卷ID参数SQL注入"""
        malicious_ids = [
            "1 OR 1=1",
            "1 UNION SELECT * FROM users--",
            "1; DROP TABLE surveys--"
        ]
        
        for malicious_id in malicious_ids:
            response = client.get(f"/api/v1/surveys/{malicious_id}")
            # 应该返回404或422，而不是泄露数据
            assert response.status_code in [404, 422]

    def test_sql_injection_in_search(self, client, auth_headers):
        """测试搜索功能SQL注入"""
        search_terms = [
            "test' OR '1'='1",
            "test' UNION SELECT * FROM users--",
            "'; DROP TABLE surveys--"
        ]
        
        for term in search_terms:
            response = client.get(
                "/api/v1/surveys/",
                params={"search": term},
                headers=auth_headers
            )
            # 搜索应该正常或返回空结果，不应该泄露数据库信息
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                # 确保返回的数据不是用户表
                data = response.json()
                for item in data:
                    assert "hashed_password" not in item
