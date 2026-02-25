#!/usr/bin/env python3
"""
使用SQLite数据库的简化main.py，用于本地测试前端功能
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# 简化的数据库配置
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 创建SQLite数据库
engine = create_engine("sqlite:///./survey.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建简单的数据模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

# 创建表
Base.metadata.create_all(bind=engine)

# FastAPI应用初始化
app = FastAPI(
    title="Survey Product Document API",
    description="API for managing surveys, questions, answers, users, and organizations.",
    version="0.1.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
STATIC_FRONTEND_DIR = "frontend/dist"
if os.path.isdir(STATIC_FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_FRONTEND_DIR, "assets")), name="assets")

# 简化的API路由
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Survey API is running",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/v1/users/me")
def get_current_user():
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True
    }

@app.get("/api/v1/users/")
def get_users():
    return [
        {"id": 1, "username": "admin", "email": "admin@example.com"},
        {"id": 2, "username": "test_user", "email": "test@example.com"}
    ]

@app.post("/api/v1/users/login/access-token")
def login():
    return {"access_token": "test_token", "token_type": "bearer"}

@app.get("/api/v1/surveys/")
def get_surveys():
    return [
        {
            "id": 1,
            "title": "测试调研1",
            "description": "这是一个测试调研",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        },
        {
            "id": 2,
            "title": "测试调研2", 
            "description": "这是另一个测试调研",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
    ]

@app.post("/api/v1/surveys/")
def create_survey():
    return {
        "id": 3,
        "title": "新创建的调研",
        "description": "通过API创建的调研",
        "created_at": datetime.datetime.now().isoformat()
    }

@app.get("/api/v1/questions/")
def get_questions():
    return [
        {
            "id": 1,
            "text": "您对工作环境满意吗？",
            "type": "SINGLE_CHOICE",
            "options": '[{"text": "满意", "score": 5}, {"text": "不满意", "score": 1}]',
            "is_required": True
        },
        {
            "id": 2,
            "text": "您希望改进哪些方面？",
            "type": "MULTI_CHOICE",
            "options": '[{"text": "薪资", "score": 1}, {"text": "环境", "score": 1}]',
            "is_required": False
        }
    ]

@app.post("/api/v1/questions/")
def create_question():
    return {
        "id": 3,
        "text": "新创建的问题",
        "type": "TEXT_INPUT",
        "is_required": True
    }

@app.get("/api/v1/tags/")
def get_tags():
    return [
        {"id": 1, "name": "工作环境", "color": "#409EFF", "description": "工作相关标签"},
        {"id": 2, "name": "薪资福利", "color": "#67C23A", "description": "薪资相关标签"}
    ]

@app.post("/api/v1/tags/")
def create_tag():
    return {
        "id": 3,
        "name": "新标签",
        "color": "#E6A23C",
        "description": "通过API创建的标签"
    }

@app.get("/api/v1/organizations/")
def get_organizations():
    return [
        {"id": 1, "name": "科技公司", "description": "科技相关的公司"},
        {"id": 2, "name": "制造企业", "description": "制造业相关的公司"}
    ]

# Catch-all路由用于SPA
@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    index_file = os.path.join(STATIC_FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(status_code=404, content={"detail": "Index file not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)