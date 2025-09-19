#!/bin/bash

# 项目依赖安装脚本
# 用于快速安装后端和前端的所有依赖

echo "🚀 开始安装项目依赖..."

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version

# 检查Node.js版本
echo "📋 检查Node.js版本..."
node --version
npm --version

# 创建虚拟环境（如果不存在）
echo "🐍 设置Python虚拟环境..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
else
    echo "虚拟环境已存在"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install

# 返回根目录
cd ..

echo "✅ 依赖安装完成！"
echo ""
echo "📝 使用说明："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动后端服务: cd backend && python -m uvicorn app.main:app --reload"
echo "3. 启动前端服务: cd frontend && npm run dev"
echo ""
echo "🎉 项目依赖安装完成！"
