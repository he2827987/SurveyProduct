# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict # Pydantic V2 的正确导入
from datetime import timedelta
import os

class Settings(BaseSettings):
    # 数据库配置
    # 优先使用环境变量，如果没有则使用默认值
    DATABASE_URL: str = "mysql+pymysql://testuser:testpass@127.0.0.1:3306/survey_db"
    
    # 生产环境数据库配置支持
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "testuser"
    MYSQL_PASSWORD: str = "testpass"
    MYSQL_DATABASE: str = "survey_db"

    # JWT 配置
    SECRET_KEY: str = "anata-dake-wo-oboe-te-iru-kumo-no-kage-ga-nagere-te-yuku-kotoba-dake-ga-afure-te-iru-omoide-ha-natsukaze-yurare-nagara" # 生产环境中请务必使用强随机密钥
    # SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM 配置
    # OPENROUTER_API_KEY: str = os.getenv("sk-or-v1-...", "") # 错误的写法
    OPENROUTER_API_KEY: str # Pydantic 会自动从 .env 文件或环境变量中查找 OPENROUTER_API_KEY

    # 使用 Pydantic V2 的 SettingsConfigDict 来配置
    # 这会告诉 Pydantic 去哪里找 .env 文件
    model_config = SettingsConfigDict(
        env_file=["backend/.env", ".env", "../backend/.env"],  # 尝试多个路径
        env_file_encoding="utf-8", # 指定 .env 文件编码
        extra="ignore"        # 忽略 .env 中未定义的变量
    )

# 手动加载.env文件
def load_env_manually():
    """手动加载.env文件"""
    env_paths = [
        "backend/.env",
        ".env", 
        "../backend/.env",
        os.path.join(os.path.dirname(__file__), "..", ".env")
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip('"')

# 在创建Settings实例之前加载环境变量
load_env_manually()

# 实例化配置对象
settings = Settings()

def get_database_url():
    """动态构建数据库URL，优先使用环境变量"""
    # 如果环境变量中有完整的DATABASE_URL，直接使用
    if os.getenv("DATABASE_URL") and not os.getenv("DATABASE_URL").startswith("mysql+pymysql://testuser"):
        return os.getenv("DATABASE_URL")
    
    # 否则使用单独的MySQL配置构建URL
    mysql_host = os.getenv("MYSQL_HOST", settings.MYSQL_HOST)
    mysql_port = os.getenv("MYSQL_PORT", str(settings.MYSQL_PORT))
    mysql_user = os.getenv("MYSQL_USER", settings.MYSQL_USER)
    mysql_password = os.getenv("MYSQL_PASSWORD", settings.MYSQL_PASSWORD)
    mysql_database = os.getenv("MYSQL_DATABASE", settings.MYSQL_DATABASE)
    
    return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# 更新DATABASE_URL
settings.DATABASE_URL = get_database_url()

# --- 调试信息 ---
# 为了确认 settings 是否加载成功，可以在实例化后打印
api_key_preview = settings.OPENROUTER_API_KEY[:10] + "..." if len(settings.OPENROUTER_API_KEY) > 10 else "Too_Short/Empty"
print(f"[Config Module] Final settings.OPENROUTER_API_KEY (preview): {api_key_preview}")
print(f"[Config Module] DATABASE_URL: {settings.DATABASE_URL}")
print(f"[Config Module] Environment: {os.getenv('ENVIRONMENT', 'development')}")
# --- 调试信息结束 ---
