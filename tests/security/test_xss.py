"""
安全测试 - XSS攻击
"""
import pytest


class TestXSS:
    """XSS攻击测试"""

    def test_xss_in_survey_title(self, client, auth_headers):
        """测试问卷标题XSS"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = client.post(
                "/api/v1/surveys/",
                headers=auth_headers,
                json={
                    "title": payload,
                    "description": "测试XSS"
                }
            )
            
            if response.status_code == 200:
                # 获取创建的问卷
                survey_id = response.json().get("id")
                get_response = client.get(f"/api/v1/surveys/{survey_id}")
                
                # 确保返回的数据中XSS脚本被转义
                data = get_response.json()
                assert "<script>" not in data.get("title", "")
                assert "onerror=" not in data.get("title", "")
                assert "onload=" not in data.get("title", "")

    def test_xss_in_question_text(self, client, auth_headers):
        """测试题目文本XSS"""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = client.post(
            "/api/v1/questions/",
            headers=auth_headers,
            json={
                "text": xss_payload,
                "type": "text_input"
            }
        )
        
        if response.status_code == 200:
            question_id = response.json().get("id")
            get_response = client.get(f"/api/v1/questions/{question_id}")
            
            data = get_response.json()
            assert "<script>" not in data.get("text", "")

    def test_xss_in_answer_text(self, client):
        """测试答案文本XSS"""
        xss_payload = "<img src=x onerror=alert('XSS')>"
        
        response = client.post(
            "/api/v1/surveys/1/answers",
            json={
                "survey_id": 1,
                "question_id": 1,
                "answer_text": xss_payload,
                "score": 3
            }
        )
        
        if response.status_code == 200:
            # 获取答案列表
            get_response = client.get("/api/v1/surveys/1/answers")
            data = get_response.json()
            
            # 检查XSS是否被转义
            for answer in data:
                assert "onerror=" not in answer.get("answer_text", "")

    def test_xss_in_user_profile(self, client, auth_headers):
        """测试用户信息XSS"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = client.put(
                "/api/v1/users/me",
                headers=auth_headers,
                json={"email": payload}
            )
            
            # 应该被拒绝或转义
            if response.status_code == 200:
                get_response = client.get("/api/v1/users/me", headers=auth_headers)
                data = get_response.json()
                assert "<script>" not in data.get("email", "")

    def test_xss_content_type_header(self, client):
        """测试Content-Type头部注入"""
        malicious_types = [
            "text/html",
            "text/html; charset=UTF-8",
            "text/html; <script>alert('XSS')</script>"
        ]
        
        for content_type in malicious_types:
            response = client.post(
                "/api/v1/users/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123"
                },
                headers={"Content-Type": content_type}
            )
            # 应该拒绝或忽略不正确的Content-Type
            assert response.status_code in [200, 415, 422]
