# backend/app/main.py

import os
print("--- FastAPI App Startup Debug ---")
print(f"1. Current Working Directory: {os.getcwd()}")
print(f"2. __file__ of main.py: {__file__}")
print(f"3. OPENROUTER_API_KEY in os.environ (preview): {os.environ.get('OPENROUTER_API_KEY', 'NOT_FOUND')[:15] + '...' if len(os.environ.get('OPENROUTER_API_KEY', '')) > 15 else 'Too_Short/Not_Found'}")
print("--- End Debug ---")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import user_api
from backend.app.api import survey_api
from backend.app.api import question_api
from backend.app.api import answer_api
from backend.app.api import org_api
from backend.app.api import llm_api
from backend.app.api import department_api
from backend.app.api import participant_api
from backend.app.api import analytics_api, category_api, tag_api, analysis_api

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Survey Product Document API",
    description="API for managing surveys, questions, answers, users, and organizations.",
    version="0.1.0",
)

# 添加 CORS 中间件
origins = [
    "http://localhost:5173", # Vite 默认端口
    "http://localhost:8080", # Vue CLI 默认端口 (如果适用)
    "http://127.0.0.1:5173", # 也允许 127.0.0.1 形式
    # 你可以添加其他需要允许的源，例如生产环境的域名
    # "https://yourdomain.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 注册 API 路由
app.include_router(user_api.router, tags=["user"], prefix="/api/v1")
app.include_router(survey_api.router, tags=["survey"], prefix="/api/v1")
app.include_router(question_api.router, tags=["question"], prefix="/api/v1")
app.include_router(answer_api.router, tags=["answer"], prefix="/api/v1")
app.include_router(llm_api.router, tags=["llm"], prefix="/api/v1")
app.include_router(org_api.router, tags=["organization"], prefix="/api/v1")
app.include_router(department_api.router, tags=["department"], prefix="/api/v1")
app.include_router(participant_api.router, tags=["participant"], prefix="/api/v1")
app.include_router(analytics_api.router, tags=["analytics"], prefix="/api/v1")
app.include_router(category_api.router, tags=["category"], prefix="/api/v1")
app.include_router(tag_api.router, tags=["tag"], prefix="/api/v1")
app.include_router(analysis_api.router, tags=["analysis"], prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Survey Product Document API!"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint working!"}

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Survey API is running",
        "timestamp": "2024-01-01T00:00:00Z"
    }

