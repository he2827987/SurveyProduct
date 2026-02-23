#!/usr/bin/env python3
"""
创建基本的PostgreSQL表结构
"""

import os
os.environ['OPENROUTER_API_KEY'] = "test-key"

from sqlalchemy import create_engine, text

# 数据库连接URL
DATABASE_URL = "postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com:5432/surveyproduct_db"

def create_basic_tables():
    """创建基本表结构"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("创建基本表结构...")
            
            # 创建用户表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建组织表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    owner_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建问题表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS questions (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    options TEXT,
                    is_required BOOLEAN DEFAULT FALSE,
                    owner_id INTEGER,
                    organization_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建调查表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS surveys (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_by_user_id INTEGER NOT NULL,
                    organization_id INTEGER,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建调查问题关联表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS survey_questions (
                    id SERIAL PRIMARY KEY,
                    survey_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    "order" INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建调查回答表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS survey_answers (
                    id SERIAL PRIMARY KEY,
                    survey_id INTEGER,
                    user_id INTEGER,
                    answers TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建alembic版本表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    PRIMARY KEY (version_num)
                )
            """))
            
            # 插入alembic版本
            conn.execute(text("""
                INSERT INTO alembic_version (version_num) 
                VALUES ('1a2b3c4d5e6f')
                ON CONFLICT (version_num) DO NOTHING
            """))
            
            conn.commit()
            print("✅ 基本表结构创建成功!")
            
            # 检查表是否创建成功
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"创建的表: {tables}")
            
    except Exception as e:
        print(f"❌ 创建表失败: {e}")

if __name__ == "__main__":
    create_basic_tables()