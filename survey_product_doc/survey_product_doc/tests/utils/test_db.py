#!/usr/bin/env python3
"""
数据库连接测试
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.database import SessionLocal
from backend.app.models.user import User

def test_db_connection():
    """测试数据库连接"""
    try:
        db = SessionLocal()
        print("数据库连接成功")
        
        # 测试查询用户
        users = db.query(User).all()
        print(f"找到 {len(users)} 个用户")
        
        for user in users:
            print(f"用户: {user.username} (ID: {user.id})")
        
        db.close()
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_db_connection()
