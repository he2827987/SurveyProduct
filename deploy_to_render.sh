#!/bin/bash

# SurveyProduct Render 部署脚本
# 用于快速部署到 Render 云端

echo "🚀 SurveyProduct Render 部署脚本"
echo "=================================="

# 检查是否在正确的目录
if [ ! -f "render.yaml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Git 状态
echo "📋 检查 Git 状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: 有未提交的更改"
    read -p "是否继续部署? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 部署已取消"
        exit 1
    fi
fi

# 提交更改
echo "📝 提交更改..."
git add .
git commit -m "准备 Render 部署: 添加云端部署配置

- 添加 render.yaml 配置文件
- 更新 config.py 支持生产环境
- 添加数据库初始化脚本
- 创建部署指南文档"

# 推送到 GitHub
echo "📤 推送到 GitHub..."
git push origin main

echo "✅ 代码已推送到 GitHub"
echo ""
echo "🎯 下一步操作:"
echo "1. 访问 https://dashboard.render.com"
echo "2. 点击 'New +' → 'Web Service'"
echo "3. 连接你的 GitHub 仓库"
echo "4. 使用以下配置:"
echo ""
echo "   Name: survey-product-backend"
echo "   Environment: Python 3"
echo "   Build Command: cd survey_product_doc && pip install -r requirements.txt && python backend/init_database.py"
echo "   Start Command: cd survey_product_doc && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "5. 配置环境变量 (参考 RENDER_DEPLOYMENT_GUIDE.md)"
echo "6. 部署完成!"
echo ""
echo "📚 详细说明请查看: RENDER_DEPLOYMENT_GUIDE.md"
