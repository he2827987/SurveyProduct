#!/bin/bash

# 启动后端服务的脚本

echo "正在启动后端服务..."

# 检查虚拟环境是否存在
if [ ! -d "survey_backend_venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境并启动服务
source survey_backend_venv/bin/activate

# 检查依赖是否安装
if ! python -c "import pydantic_settings" 2>/dev/null; then
    echo "❌ pydantic_settings 未安装，正在安装依赖..."
    pip install -r backend/requirements.txt
fi

# 启动后端服务
echo "✅ 启动后端服务..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
