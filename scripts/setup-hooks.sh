#!/bin/bash
# 安装 Git hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}安装 Git hooks...${NC}"

# 检查是否是 Git 仓库
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${YELLOW}初始化 Git 仓库...${NC}"
    cd "$PROJECT_ROOT"
    git init
    echo -e "${GREEN}✓ Git 仓库已初始化${NC}"
fi

# 创建 .git/hooks 目录（如果不存在）
mkdir -p "$PROJECT_ROOT/.git/hooks"

# 安装 pre-commit hook
if [ -f "$SCRIPT_DIR/pre-commit-hook.sh" ]; then
    cp "$SCRIPT_DIR/pre-commit-hook.sh" "$PROJECT_ROOT/.git/hooks/pre-commit"
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
    echo -e "${GREEN}✓ pre-commit hook 已安装${NC}"
else
    echo -e "${YELLOW}⚠️  找不到 pre-commit-hook.sh${NC}"
fi

# 给脚本添加执行权限
chmod +x "$SCRIPT_DIR/switch-env.sh" 2>/dev/null || true

echo -e "${GREEN}✅ Git hooks 安装完成！${NC}"
echo ""
echo "现在在每次 git commit 前，系统会自动检查环境配置"
