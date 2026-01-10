#!/usr/bin/env python3
"""
测试配置加载的脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.app.config import settings
    print("✅ 配置加载成功!")
    print(f"OPENROUTER_API_KEY: {settings.OPENROUTER_API_KEY[:20]}..." if settings.OPENROUTER_API_KEY else "未设置")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
