# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict # Pydantic V2 的正确导入
from datetime import timedelta
import os

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root@localhost:3306/survey_db"
    # 或者更简洁地写成
    # DATABASE_URL: str

    # JWT 配置
    SECRET_KEY: str = "anata-dake-wo-oboe-te-iru-kumo-no-kage-ga-nagere-te-yuku-kotoba-dake-ga-afure-te-iru-omoide-ha-natsukaze-yurare-nagara" # 生产环境中请务必使用强随机密钥
    # SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

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

# --- 调试信息 ---
# 为了确认 settings 是否加载成功，可以在实例化后打印
api_key_preview = settings.OPENROUTER_API_KEY[:10] + "..." if len(settings.OPENROUTER_API_KEY) > 10 else "Too_Short/Empty"
print(f"[Config Module] Final settings.OPENROUTER_API_KEY (preview): {api_key_preview}")
print(f"[Config Module] DATABASE_URL: {settings.DATABASE_URL}")
# --- 调试信息结束 ---
