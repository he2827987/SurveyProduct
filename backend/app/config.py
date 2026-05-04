# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict # Pydantic V2 的正确导入
from datetime import timedelta
import os

class Settings(BaseSettings):
    # 数据库配置 - 使用环境变量
    DATABASE_URL: str = "postgresql://localhost:5432/survey_db"  # 本地开发默认值
    # 在生产环境中，Render会自动设置 DATABASE_URL 环境变量

    # JWT 配置
    SECRET_KEY: str = "anata-dake-wo-oboe-te-iru-kumo-no-kage-ga-nagere-te-yuku-kotoba-dake-ga-afure-te-iru-omoide-ha-natsukaze-yurare-nagara" # 生产环境中请务必使用强随机密钥
    # SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LLM 配置
    OPENROUTER_API_KEY: str = ""  # 必须从环境变量获取

    # SMTP 邮件配置（暂时可选，未配置时验证码打印到日志）
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # 验证码配置
    RESET_CODE_EXPIRE_MINUTES: int = 10

    # 使用 Pydantic V2 的 SettingsConfigDict 来配置
    # 这会告诉 Pydantic 去哪里找 .env 文件
    _env_files = [] if os.getenv("ENVIRONMENT") == "production" else ["backend/.env", ".env", "../backend/.env"]
    model_config = SettingsConfigDict(
        env_file=_env_files,
        env_file_encoding="utf-8",
        extra="ignore"
    )

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

def load_env_manually():
    if os.getenv("ENVIRONMENT") == "production":
        return
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"')
    else:
        env_paths = [
            "backend/.env",
            ".env",
            "../backend/.env",
        ]
        for env_path in env_paths:
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value.strip('"')
                break

load_env_manually()

# 实例化配置对象
settings = Settings()

print(f"[Config] ENVIRONMENT={os.getenv('ENVIRONMENT', 'NOT SET')}")
print(f"[Config] DATABASE_URL={settings.DATABASE_URL[:50]}...")
print(f"[Config] ENVIRON DATABASE_URL={os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")

# --- 调试信息 ---
# 生产环境中可以关闭调试信息，但本地开发时有用
if os.getenv("ENVIRONMENT") != "production":
    api_key_preview = settings.OPENROUTER_API_KEY[:10] + "..." if len(settings.OPENROUTER_API_KEY) > 10 else "Too_Short/Empty"
    print(f"[Config Module] Final settings.OPENROUTER_API_KEY (preview): {api_key_preview}")
    print(f"[Config Module] DATABASE_URL: {settings.DATABASE_URL}")
# --- 调试信息结束 ---
