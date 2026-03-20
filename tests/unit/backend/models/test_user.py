"""
用户模型单元测试
"""
import pytest
from backend.app.models import User
from backend.app.security import get_password_hash


class TestUserModel:
    """用户模型测试"""

    def test_create_user_success(self):
        """测试成功创建用户"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpass123"),
            role="researcher"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "researcher"
        assert user.is_active is True

    def test_user_default_values(self):
        """测试用户默认值"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpass123")
        )
        assert user.role == "researcher"
        assert user.is_active is True
        assert user.manager_id is None

    def test_user_invalid_role(self):
        """测试无效角色"""
        with pytest.raises(Exception):
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("testpass123"),
                role="invalid_role"
            )

    def test_user_email_uniqueness(self, db_session):
        """测试邮箱唯一性"""
        user1 = User(
            username="user1",
            email="same@example.com",
            hashed_password=get_password_hash("pass123")
        )
        user2 = User(
            username="user2",
            email="same@example.com",
            hashed_password=get_password_hash("pass123")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # 尝试添加相同邮箱的用户
        with pytest.raises(Exception):
            db_session.add(user2)
            db_session.commit()

    def test_user_username_uniqueness(self, db_session):
        """测试用户名唯一性"""
        user1 = User(
            username="sameuser",
            email="user1@example.com",
            hashed_password=get_password_hash("pass123")
        )
        user2 = User(
            username="sameuser",
            email="user2@example.com",
            hashed_password=get_password_hash("pass123")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # 尝试添加相同用户名的用户
        with pytest.raises(Exception):
            db_session.add(user2)
            db_session.commit()

    def test_user_manager_relationship(self, db_session):
        """测试用户上下级关系"""
        manager = User(
            username="manager",
            email="manager@example.com",
            hashed_password=get_password_hash("pass123")
        )
        employee = User(
            username="employee",
            email="employee@example.com",
            hashed_password=get_password_hash("pass123"),
            manager_id=manager.id
        )
        
        db_session.add(manager)
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)
        
        assert employee.manager_id == manager.id

    def test_user_deactivate(self, db_session):
        """测试用户停用"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("pass123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        user.is_active = False
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active is False

    def test_user_role_admin(self):
        """测试管理员角色"""
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role="admin"
        )
        assert user.role == "admin"

    def test_user_role_participant(self):
        """测试参与者角色"""
        user = User(
            username="participant",
            email="participant@example.com",
            hashed_password=get_password_hash("pass123"),
            role="participant"
        )
        assert user.role == "participant"

    def test_user_organization_relationship(self, db_session):
        """测试用户组织关系"""
        from backend.app.models import Organization
        
        org = Organization(
            name="测试组织",
            description="测试",
            owner_id=1
        )
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("pass123"),
            organization_id=org.id
        )
        
        db_session.add(org)
        db_session.add(user)
        db_session.commit()
        
        assert user.organization_id == org.id
