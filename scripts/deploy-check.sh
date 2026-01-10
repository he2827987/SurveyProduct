#!/bin/bash
# 部署前环境配置检查脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              🔍 部署前配置检查                                    ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════════════════════════════════╣${NC}"
echo ""

# 检查后端配置
echo -e "${YELLOW}检查后端配置...${NC}"
if [ -f "$PROJECT_ROOT/.env" ]; then
    if grep -q "localhost" "$PROJECT_ROOT/.env"; then
        echo -e "${RED}❌ 检测到本地配置${NC}"
        echo "   DATABASE_URL 指向 localhost"
        echo ""
        echo -e "${YELLOW}⚠️  警告：使用本地配置无法部署到生产环境${NC}"
        echo ""
        echo "请运行以下命令切换到生产配置："
        echo -e "${GREEN}  ./scripts/switch-env.sh production${NC}"
        echo ""
        exit 1
    elif grep -q "aliyuncs.com\|onrender.com" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓ 生产环境配置${NC}"
        grep "DATABASE_URL" "$PROJECT_ROOT/.env" | sed 's/=.*/=***/'
    fi
else
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    exit 1
fi

# 检查前端配置
echo ""
echo -e "${YELLOW}检查前端配置...${NC}"
if [ -f "$PROJECT_ROOT/frontend/.env.production" ]; then
    if grep -q "onrender.com" "$PROJECT_ROOT/frontend/.env.production"; then
        echo -e "${GREEN}✓ 前端生产配置正确${NC}"
        cat "$PROJECT_ROOT/frontend/.env.production"
    else
        echo -e "${RED}❌ 前端生产配置不正确${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  找不到 frontend/.env.production${NC}"
fi

# 检查Git状态
echo ""
echo -e "${YELLOW}检查Git状态...${NC}"
cd "$PROJECT_ROOT"
if [ -d ".git" ]; then
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠️  有未提交的更改${NC}"
        git status --short | head -10
    else
        echo -e "${GREEN}✓ 工作区干净${NC}"
    fi
else
    echo -e "${RED}❌ 不是Git仓库${NC}"
fi

echo ""
echo -e "${BLUE}╠═══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║              ✅ 检查完成                                          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🎉 配置检查通过，可以安全部署！${NC}"
echo ""
echo "下一步："
echo "  1. git push origin main"
echo "  2. 等待 Render 自动部署"
echo "  3. 部署后运行: ./scripts/switch-env.sh local"
