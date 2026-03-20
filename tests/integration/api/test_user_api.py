"""
用户API集成测试
"""
import pytest
from fastapi.testclient import TestClient


class TestUserAPI:
    """用户API测试"""

    def test_register_user_success(self, client):
        """测试成功注册用户"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert data["username"] == "newuser"
        assert "email" in data
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data  # 不返回密码

    def test_register_duplicate_username(self, client, test_user):
        """测试注册重复用户名"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user):
        """测试注册重复邮箱"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "different_user",
                "email": test_user.email,
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_missing_username(self, client):
        """测试注册缺少用户名"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "email": "user@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # 验证错误

    def test_register_missing_email(self, client):
        """测试注册缺少邮箱"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """测试注册缺少密码"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "user@example.com"
            }
        )
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """测试注册无效邮箱"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "invalid_email",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_login_success(self, client, test_admin):
        """测试成功登录"""
        response = client.post(
            "/api/v1/users/login/access-token",
            data={
                "username": test_admin.username,
                "password": "admin123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_username(self, client):
        """测试错误用户名登录"""
        response = client.post(
            "/api/v1/users/login/access-token",
            data={
                "username": "wronguser",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_wrong_password(self, client, test_user):
        """测试错误密码登录"""
        response = client.post(
            "/api/v1/users/login/access-token",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers, test_admin):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_admin.username
        assert data["email"] == test_admin.email

    def test_get_current_user_unauthorized(self, client):
        """测试未认证访问当前用户"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """测试无效token访问"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_update_current_user(self, client, auth_headers, test_admin):
        """测试更新当前用户信息"""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "email": "updated@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"

    def test_update_current_user_unauthorized(self, client, test_admin):
        """测试未认证更新用户"""
        response = client.put(
            "/api/v1/users/me",
            json={
                "email": "updated@example.com"
            }
        )
        assert response.status_code == 401

    def test_update_user_duplicate_email(self, client, auth_headers, test_admin, test_user):
        """测试更新为重复邮箱"""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "email": test_user.email
            }
        )
        assert response.status_code == 400

    def test_logout(self, client, auth_headers):
        """测试登出"""
        response = client.post("/api/v1/users/logout", headers=auth_headers)
        # 登出通常是客户端行为，后端可能只返回成功状态
        assert response.status_code in [200, 202]
