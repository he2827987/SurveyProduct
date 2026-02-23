#!/usr/bin/env python3
"""
测试数据库连接脚本
"""

import os
os.environ['DATABASE_URL'] = "postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com:5432/surveyproduct_db"
os.environ['OPENROUTER_API_KEY'] = "test-key"

from sqlalchemy import create_engine, text

try:
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ 数据库连接成功!")
        print(f"PostgreSQL版本: {version}")
        
        # 检查表是否存在
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"现有表: {tables}")
        
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")