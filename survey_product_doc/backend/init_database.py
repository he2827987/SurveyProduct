#!/usr/bin/env python3
"""
数据库初始化脚本
用于在 Render 部署时初始化数据库表结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import engine, Base
from backend.app.config import settings

def init_database():
    """初始化数据库表结构"""
    try:
        print("🚀 开始初始化数据库...")
        print(f"📊 数据库连接: {settings.DATABASE_URL}")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建成功!")
        print("📋 已创建的表:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        print("🔍 检查数据库连接...")
        
        # 尝试连接数据库
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("✅ 数据库连接成功!")
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🗄️  SurveyProduct 数据库初始化")
    print("=" * 50)
    
    # 检查数据库连接
    if not check_database_connection():
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 数据库初始化完成!")
    print("=" * 50)
