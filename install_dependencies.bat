@echo off
REM 项目依赖安装脚本 (Windows版本)
REM 用于快速安装后端和前端的所有依赖

echo 🚀 开始安装项目依赖...

REM 检查Python版本
echo 📋 检查Python版本...
python --version

REM 检查Node.js版本
echo 📋 检查Node.js版本...
node --version
npm --version

REM 创建虚拟环境（如果不存在）
echo 🐍 设置Python虚拟环境...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
) else (
    echo 虚拟环境已存在
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
python -m pip install --upgrade pip

REM 安装Python依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt

REM 安装前端依赖
echo 📦 安装前端依赖...
cd frontend
npm install

REM 返回根目录
cd ..

echo ✅ 依赖安装完成！
echo.
echo 📝 使用说明：
echo 1. 激活虚拟环境: venv\Scripts\activate.bat
echo 2. 启动后端服务: cd backend ^&^& python -m uvicorn app.main:app --reload
echo 3. 启动前端服务: cd frontend ^&^& npm run dev
echo.
echo 🎉 项目依赖安装完成！
pause
