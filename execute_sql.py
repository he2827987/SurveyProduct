#!/usr/bin/env python3
"""
直接执行PostgreSQL SQL脚本
"""

import os
os.environ['OPENROUTER_API_KEY'] = "test-key"

from sqlalchemy import create_engine, text

# 数据库连接URL
DATABASE_URL = "postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com:5432/surveyproduct_db"

def execute_sql_file(file_path):
    """执行SQL文件"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # 读取SQL文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL
        with engine.connect() as conn:
            # 分割SQL语句并执行
            sql_statements = sql_content.split(';')
            for statement in sql_statements:
                if statement.strip():
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"执行语句失败: {e}")
                        print(f"语句内容: {statement[:100]}...")
                        
        print("✅ SQL脚本执行成功!")
        
        # 检查表是否创建成功
        with engine.connect() as conn:
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"创建的表: {tables}")
            
    except Exception as e:
        print(f"❌ 执行SQL脚本失败: {e}")

if __name__ == "__main__":
    execute_sql_file("postgresql_schema.sql")