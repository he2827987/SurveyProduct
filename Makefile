.PHONY: help local prod check-prod status

help:
	@echo "Survey Product 开发工作流"
	@echo ""
	@echo "环境切换:"
	@echo "  make local      - 切换到本地环境"
	@echo "  make prod       - 切换到生产环境"
	@echo "  make check-prod - 检查生产配置"
	@echo ""
	@echo "查看状态:"
	@echo "  make status     - 查看服务和配置状态"

local:
	./scripts/switch-env.sh local

prod:
	./scripts/switch-env.sh production

check-prod:
	./scripts/deploy-check.sh

status:
	@echo "当前配置:"
	@cat .env | grep -E "DATABASE_URL|VITE_API" | sed 's/\(DATABASE_URL.*@\).*\(@.*\)/\1***\2/'
