#!/bin/bash
# 环境配置切换脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

usage() {
    echo "用法: $0 [local|production]"
    echo ""
    echo "切换环境配置："
    echo "  local       - 切换到本地开发环境"
    echo "  production  - 切换到线上生产环境"
    echo ""
    exit 1
}

switch_to_local() {
    echo -e "${YELLOW}切换到本地开发环境...${NC}"
    
    # 后端配置
    if [ -f "$PROJECT_ROOT/.env.local" ]; then
        cp "$PROJECT_ROOT/.env.local" "$PROJECT_ROOT/.env"
        echo -e "${GREEN}✓${NC} 后端配置已切换到本地"
    else
        echo -e "${RED}✗${NC} 找不到 .env.local 文件"
        exit 1
    fi
    
    # 前端配置（确保使用 .env.development）
    if [ -f "$PROJECT_ROOT/frontend/.env.development" ]; then
        echo -e "${GREEN}✓${NC} 前端使用 .env.development (本地)"
    else
        echo -e "${YELLOW}⚠${NC}  找不到 frontend/.env.development"
    fi
    
    echo -e "${GREEN}✅ 已切换到本地开发环境${NC}"
    echo ""
    echo "后端配置："
    grep "DATABASE_URL" "$PROJECT_ROOT/.env" | sed 's/=.*/=***/' || true
    grep "VITE_API_BASE_URL" "$PROJECT_ROOT/.env" || true
}

switch_to_production() {
    echo -e "${YELLOW}切换到线上生产环境...${NC}"
    
    # 后端配置
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        cp "$PROJECT_ROOT/.env.production" "$PROJECT_ROOT/.env"
        echo -e "${GREEN}✓${NC} 后端配置已切换到生产环境"
    else
        echo -e "${RED}✗${NC} 找不到 .env.production 文件"
        exit 1
    fi
    
    # 提醒前端配置
    echo -e "${GREEN}✓${NC} 前端使用 .env.production (生产)"
    
    echo -e "${GREEN}✅ 已切换到生产环境${NC}"
    echo ""
    echo "后端配置："
    grep "DATABASE_URL" "$PROJECT_ROOT/.env" | sed 's/=.*/=***/' || true
    grep "VITE_API_BASE_URL" "$PROJECT_ROOT/.env" || true
    
    echo ""
    echo -e "${YELLOW}⚠️  注意：确保在部署前提交此更改${NC}"
}

# 主逻辑
if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    local)
        switch_to_local
        ;;
    production|prod)
        switch_to_production
        ;;
    *)
        echo -e "${RED}错误：未知的环境 '$1'${NC}"
        echo ""
        usage
        ;;
esac
