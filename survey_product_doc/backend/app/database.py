# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

# 使用配置文件中的数据库连接字符串
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建 SQLAlchemy 引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # echo=True, # 在开发阶段可以开启，用于打印所有执行的 SQL 语句，方便调试
    pool_pre_ping=True # 保持数据库连接活跃，防止连接超时
)

# 创建 SessionLocal 类，用于创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类，用于声明 ORM 模型
Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
