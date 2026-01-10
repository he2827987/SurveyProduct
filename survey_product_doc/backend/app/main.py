# backend/app/main.py

# ---------------------------------------------------------------------------
# IMPORTANT: Make sure this file is located at backend/app/main.py relative
# to your project's root directory.
#
# For Render deployment, the command executed is often `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
#
# Ensure your frontend is built using `npm run build` (or similar) and outputs
# static files (index.html, JS, CSS, etc.) into a predictable directory.
# ---------------------------------------------------------------------------

import logging
import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- 1. 导入 StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager

# ===== 配置日志系统 =====
# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)  # 输出到标准输出
    ]
)

# 获取应用日志记录器
logger = logging.getLogger(__name__)

# --- Lifespan 事件处理器 ---
# 这将触发 uvicorn 的生命周期日志输出
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - 在应用启动前执行
    logger.info("=" * 60)
    logger.info("🚀 Survey Product API lifespan startup...")
    logger.info("=" * 60)

    # 在这里可以执行应用初始化逻辑
    # yield 后 uvicorn 会输出 "Application startup complete."
    yield

    # Shutdown - 在应用关闭时执行
    logger.info("🛑 Survey Product API lifespan shutdown...")

logger.info("✅ Lifespan 事件处理器已配置")

# --- 导入你的数据库模型和API路由 ---
# 确保你的数据库配置和API路由导入是正确的
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

# --- 数据库初始化 ---
# 这一步会确保你的数据库表被创建。
# 在生产环境中，可能更倾向于使用 alembic 或其他迁移工具。
def run_alembic_migrations():
    """
    Run pending Alembic migrations before the app starts.
    """
    try:
        root_dir = Path(__file__).resolve().parents[2]
        alembic_cfg = Config(root_dir / "alembic.ini")
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(alembic_cfg, "head")
    except Exception as exc:  # pragma: no cover
        logging.warning("Unable to run alembic migrations automatically: %s", exc)


run_alembic_migrations()
Base.metadata.create_all(bind=engine)
logger.info("✅ 数据库迁移完成")

# --- FastAPI 应用初始化 ---
app = FastAPI(
    title="Survey Product Document API",
    description="API for managing surveys, questions, answers, users, and organizations.",
    version="0.1.0",
    lifespan=lifespan,  # 添加 lifespan 事件处理器
)
logger.info("✅ FastAPI 应用初始化完成")

# --- 2. 定义前端构建输出目录 ---
# !!! 非常重要 !!!
# 请根据你 'npm run build' 命令的实际输出目录进行调整。
# 假设你的项目结构是:
# /your_repo_root
#   ├── backend/
#   │   └── app/
#   │       └── main.py
#   └── survey_product_doc/
#       └── frontend/
#           ├── ... (src files)
#           └── dist/  <-- 你的 build output here
#
# 如果你的 `npm run build` 输出到 'build' 目录，请改为:
# STATIC_FRONTEND_DIR = "survey_product_doc/frontend/build"
# 如果输出到 'out' 目录，请改为:
# STATIC_FRONTEND_DIR = "survey_product_doc/frontend/out"
#
# 这里的路径是相对于 Render 部署时运行 'uvicorn' 命令的当前工作目录 (通常是项目根目录)。
STATIC_FRONTEND_DIR = "survey_product_doc/frontend/dist"

# --- CORS 中间件配置 ---
# 本地开发时用的源
local_origins = [
    "http://localhost:5173", # Vite 默认端口
    "http://localhost:8080", # Vue CLI 默认端口 (if applicable)
    "http://127.0.0.1:5173",
]

# !!! 生产环境安全建议 !!!
# 如果你的前端部署在 Render 上，并且将通过 Render 提供的 URL `https://your-service-name.onrender.com` 访问，
# 请将该 URL 添加到 origins 列表中。
# 暂时保留 "*" 和本地源，方便你在 Render initial deploy 时测试，
# 但部署成功后，请务必收紧 allow_origins，移除 "*"！
# 例如:
# render_origin = os.environ.get("RENDER_FRONTEND_URL") # 可以在 Render 环境变量中设置
# if render_origin:
#     origins.append(render_origin)
# else:
#     # Fallback or warn, depending on your setup

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", *local_origins],  # 暂时允许所有源 + 本地开发源，生产请收紧！
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)
logger.info("✅ CORS 中间件配置完成")


# --- 注册 API 路由 ---
# 这些路由都带有 "/api/v1/" 前缀，因此不会与根目录的静态文件服务冲突。
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
logger.info("✅ 所有API路由注册完成")

# --- 保留其他测试或健康检查路由 ---
# 这些路由必须在 catch-all 路由之前定义，避免被拦截
@app.get("/test")
def test_endpoint():
    logger.info("📝 测试端点请求")
    return {"message": "Test endpoint working!"}

@app.get("/api/v1/health")
def health_check():
    # 建议使用一些动态获取的时间戳，而不是硬编码
    import datetime
    logger.info("📊 健康检查请求")
    return {
        "status": "healthy",
        "message": "Survey API is running",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# --- 3. 挂载前端静态文件 ---
# 注意顺序：先注册 API，再挂载静态目录，避免 /api/* 被静态服务截获导致 404/405
# 为避免根路径 mount 抢占导致 404，这里仅挂载资源目录到 /assets
assets_dir = os.path.join(STATIC_FRONTEND_DIR, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
else:
    app.mount("/assets", StaticFiles(directory=STATIC_FRONTEND_DIR), name="assets")

# --- 4. Catch-all 路由用于 SPA 回退 ---
# 对于非 API 路径，回退到前端 index.html，避免刷新 404
# 这个路由必须在最后定义，避免拦截其他路由
@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    index_file = os.path.join(STATIC_FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(status_code=404, content={"detail": "Index file not found"})

# 注意：完整的启动日志流程：
# 1. lifespan startup 开始 -> 输出启动信息
# 2. yield -> uvicorn lifespan/on.py 第62行输出 "Application startup complete."
# 3. lifespan shutdown -> 输出关闭信息

# ✅ 已成功恢复 uvicorn 默认的启动完成日志输出

# --- END OF FILE ---
# 现在 lifespan 事件处理器会触发 uvicorn 的生命周期日志输出
