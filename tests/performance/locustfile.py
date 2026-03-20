"""
Locust性能测试脚本
测试SurveyProduct API性能
"""
from locust import HttpUser, task, between
import json


class SurveyProductUser(HttpUser):
    """模拟SurveyProduct用户"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户开始时登录获取token"""
        response = self.client.post(
            "/api/v1/users/login/access-token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def get_surveys(self):
        """获取问卷列表 (高频操作)"""
        self.client.get("/api/v1/surveys/")
    
    @task(2)
    def get_survey_detail(self):
        """获取问卷详情 (中频操作)"""
        self.client.get("/api/v1/surveys/1")
    
    @task(1)
    def get_user_info(self):
        """获取用户信息 (低频操作)"""
        if self.token:
            self.client.get("/api/v1/users/me", headers=self.headers)
    
    @task(1)
    def get_analytics(self):
        """获取分析数据 (低频操作)"""
        if self.token:
            self.client.get("/api/v1/organizations/6/analytics/overview", headers=self.headers)
    
    @task(1)
    def create_survey(self):
        """创建问卷 (低频操作)"""
        if self.token:
            survey_data = {
                "title": f"性能测试问卷_{self.user_id}",
                "description": "性能测试",
                "status": "draft"
            }
            self.client.post("/api/v1/surveys/", headers=self.headers, json=survey_data)


class SurveyProductParticipant(HttpUser):
    """模拟问卷参与者"""
    wait_time = between(2, 5)
    
    @task(5)
    def view_public_survey(self):
        """查看公开问卷"""
        self.client.get("/api/v1/surveys/1")
    
    @task(3)
    def submit_answer(self):
        """提交答案"""
        answer_data = {
            "survey_id": 1,
            "question_id": 1,
            "answer_text": "非常满意",
            "score": 5
        }
        self.client.post("/api/v1/surveys/1/answers", json=answer_data)
