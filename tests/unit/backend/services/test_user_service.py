"""
用户服务层单元测试
"""
import pytest
from unittest.mock import Mock, patch
from backend.app.services.user_service import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    authenticate_user,
    verify_password
)
from backend.app.database import get_db


class TestUserService:
    """用户服务测试"""

    def test_get_user_by_username_success(self, db_session, test_user):
        """测试通过用户名获取用户"""
        user = get_user_by_username(db_session, username=test_user.username)
        assert user is not None
        assert user.username == test_user.username
        assert user.email == test_user.email

    def test_get_user_by_username_not_found(self, db_session):
        """测试获取不存在的用户"""
        user = get_user_by_username(db_session, username="nonexistent")
        assert user is None

    def test_get_user_by_email_success(self, db_session, test_user):
        """测试通过邮箱获取用户"""
        user = get_user_by_email(db_session, email=test_user.email)
        assert user is not None
        assert user.email == test_user.email
        assert user.username == test_user.username

    def test_get_user_by_email_not_found(self, db_session):
        """测试获取不存在的邮箱"""
        user = get_user_by_email(db_session, email="nonexistent@example.com")
        assert user is None

    @patch('backend.app.services.user_service.get_password_hash')
    def test_create_user_success(self, mock_hash, db_session):
        """测试成功创建用户"""
        mock_hash.return_value = "hashed_password"
        
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "plain_password"
        }
        
        user = create_user(db_session, user_data)
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.role == "researcher"  # 默认角色

    @patch('backend.app.services.user_service.get_password_hash')
    def test_create_user_with_role(self, mock_hash, db_session):
        """测试创建带角色的用户"""
        mock_hash.return_value = "hashed_password"
        
        user_data = {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "admin_pass",
            "role": "admin"
        }
        
        user = create_user(db_session, user_data)
        assert user.role == "admin"

    def test_create_user_duplicate_username(self, db_session, test_user):
        """测试创建重复用户名"""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password"
        }
        
        with pytest.raises(Exception):
            create_user(db_session, user_data)

    def test_create_user_duplicate_email(self, db_session, test_user):
        """测试创建重复邮箱"""
        user_data = {
            "username": "different_user",
            "email": test_user.email,
            "password": "password"
        }
        
        with pytest.raises(Exception):
            create_user(db_session, user_data)

    @patch('backend.app.services.user_service.verify_password')
    def test_authenticate_user_success(self, mock_verify, db_session, test_user):
        """测试成功认证用户"""
        mock_verify.return_value = True
        
        user = authenticate_user(db_session, username=test_user.username, password="testpass")
        assert user is not None
        assert user.username == test_user.username

    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """测试错误密码认证"""
        user = authenticate_user(db_session, username=test_user.username, password="wrongpass")
        assert user is None

    def test_authenticate_user_not_found(self, db_session):
        """测试认证不存在的用户"""
        user = authenticate_user(db_session, username="nonexistent", password="anypass")
        assert user is None

    def test_verify_password_correct(self):
        """测试验证正确密码"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        plain_password = "test123"
        hashed = pwd_context.hash(plain_password)
        
        assert pwd_context.verify(plain_password, hashed) is True

    def test_verify_password_wrong(self):
        """测试验证错误密码"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        plain_password = "test123"
        wrong_password = "wrongpass"
        hashed = pwd_context.hash(plain_password)
        
        assert pwd_context.verify(wrong_password, hashed) is False

    def test_user_deactivate_account(self, db_session, test_user):
        """测试停用用户账户"""
        user = get_user_by_username(db_session, username=test_user.username)
        user.is_active = False
        db_session.commit()
        
        # 重新获取用户
        deactivated_user = get_user_by_username(db_session, username=test_user.username)
        assert deactivated_user.is_active is False

    def test_user_activate_account(self, db_session, test_user):
        """测试激活用户账户"""
        user = get_user_by_username(db_session, username=test_user.username)
        user.is_active = False
        db_session.commit()
        
        # 重新激活
        user.is_active = True
        db_session.commit()
        
        # 重新获取用户
        activated_user = get_user_by_username(db_session, username=test_user.username)
        assert activated_user.is_active is True

    def test_get_password_hash_function(self):
        """测试密码哈希函数"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt哈希通常较长
        assert isinstance(hashed, str)

    def test_hash_same_password_different_results(self):
        """测试相同密码产生不同哈希（salt机制）"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # bcrypt的salt机制确保相同密码产生不同哈希
        assert hash1 != hash2
