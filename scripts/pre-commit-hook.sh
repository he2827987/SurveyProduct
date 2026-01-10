#!/bin/bash
# Git pre-commit hook
# 在提交前自动检查并提示环境配置

set -e

# 颜色输出
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 当作为Git hook运行时，工作目录已经是项目根目录
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo -e "${YELLOW}🔍 检查环境配置...${NC}"

# 检查 .env 文件内容
if [ -f "$PROJECT_ROOT/.env" ]; then
    if grep -q "localhost:3306" "$PROJECT_ROOT/.env"; then
        echo -e "${YELLOW}⚠️  检测到本地数据库配置${NC}"
        echo ""
        echo "当前 .env 使用本地配置（localhost）"
        echo ""
        echo -e "${YELLOW}如果要部署到生产环境，请运行：${NC}"
        echo "  ./scripts/switch-env.sh production"
        echo ""
        
        # 询问是否继续
        read -p "是否继续提交？[y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}✗ 提交已取消${NC}"
            exit 1
        fi
    elif grep -q "aliyuncs.com" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓ 检测到生产环境配置${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  找不到 .env 文件${NC}"
fi

echo -e "${GREEN}✓ 环境配置检查完成${NC}"
exit 0
