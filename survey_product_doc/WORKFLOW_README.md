# 🔄 环境配置自动化工作流

## 快速开始

### 一键切换环境

```bash
# 本地开发
./scripts/switch-env.sh local

# 准备部署
./scripts/switch-env.sh production
```

## 📋 工作流说明

### 完整部署流程

```bash
# 1. 开发完成，切换到生产配置
./scripts/switch-env.sh production

# 2. 提交代码（会自动检查配置）
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到远程仓库
git push origin main

# 4. Render自动部署

# 5. 切回本地环境继续开发
./scripts/switch-env.sh local
```

### 日常开发流程

```bash
# 确保使用本地配置
./scripts/switch-env.sh local

# 启动后端（终端1）
source venv/bin/activate
python -m uvicorn backend.app.main:app --reload

# 启动前端（终端2）
cd frontend
npm run dev

# 访问: http://localhost:3000
```

## 🔍 配置检查

### 查看当前配置

```bash
# 快速查看
cat .env | grep -E "DATABASE|API_BASE"

# 详细查看
cat .env
```

### 验证环境

```bash
# 检查是否本地环境
cat .env | grep "localhost" && echo "✓ 本地环境"

# 检查是否生产环境  
cat .env | grep "aliyuncs.com" && echo "✓ 生产环境"
```

## ⚡ 快捷别名（可选）

在 `~/.zshrc` 或 `~/.bashrc` 添加：

```bash
# 环境切换别名
alias env-local='cd /path/to/project && ./scripts/switch-env.sh local'
alias env-prod='cd /path/to/project && ./scripts/switch-env.sh production'
alias env-check='cat .env | grep -E "DATABASE|API_BASE"'

# 服务启动别名
alias start-backend='source venv/bin/activate && python -m uvicorn backend.app.main:app --reload'
alias start-frontend='cd frontend && npm run dev'
```

## 📁 文件结构

```
survey_product_doc/
├── .env                    # 当前激活配置（不提交）
├── .env.local              # 本地配置模板（可提交）
├── .env.production         # 生产配置模板（可提交）
├── .env.example            # 配置示例（可提交）
├── .gitignore              # Git忽略规则
├── ENV_MANAGEMENT.md       # 详细文档
├── WORKFLOW_README.md      # 本文件
└── scripts/
    ├── switch-env.sh       # 环境切换脚本
    ├── setup-hooks.sh      # Git hooks安装
    └── pre-commit-hook.sh  # Pre-commit检查
```

## 🎯 典型场景

### 场景1：准备部署新功能

```bash
# 开发完成
git status

# 切换到生产配置
./scripts/switch-env.sh production

# 提交
git add .
git commit -m "feat: 新功能"
# 👆 会自动检查配置并提示

# 推送
git push origin main

# 部署完成后切回本地
./scripts/switch-env.sh local
```

### 场景2：紧急修复

```bash
# 快速切换到生产
./scripts/switch-env.sh prod

# 修复并提交
git add .
git commit -m "fix: 紧急修复"
git push

# 切回本地
./scripts/switch-env.sh local
```

### 场景3：克隆项目后首次设置

```bash
# 克隆项目
git clone <repo-url>
cd survey_product_doc

# 安装Git hooks
./scripts/setup-hooks.sh

# 切换到本地环境
./scripts/switch-env.sh local

# 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install

# 启动服务
./scripts/switch-env.sh local
```

## 🛡️ 安全检查清单

部署前检查：

- [ ] 代码已测试通过
- [ ] 已切换到生产配置 (`./scripts/switch-env.sh production`)
- [ ] 验证配置正确 (`cat .env | grep DATABASE`)
- [ ] Git commit时hook已执行检查
- [ ] 推送前再次确认配置

部署后检查：

- [ ] Render部署成功
- [ ] 线上服务正常
- [ ] 已切回本地配置 (`./scripts/switch-env.sh local`)
- [ ] 本地服务正常

## 💡 提示

- 🔔 **提交前**：系统会自动检查配置并提示
- 📝 **提交时**：确保commit message清晰
- 🔄 **部署后**：记得切回本地环境
- 🔒 **安全**：`.env` 已被 `.gitignore` 保护

## ❓ 常见问题

**Q: 切换环境后服务不生效？**
A: 如果后端使用 `--reload`会自动重载，否则需要手动重启

**Q: Git hook 没有执行？**
A: 运行 `./scripts/setup-hooks.sh` 重新安装

**Q: 忘记切换配置就提交了？**
A: Pre-commit hook 会提醒你，按 'N' 取消提交，切换配置后重新提交

**Q: 如何禁用 hook？**
A: 使用 `git commit --no-verify` 跳过检查（不推荐）

## 📚 相关文档

- 详细文档：`ENV_MANAGEMENT.md`
- 项目README：`README.md`
- API文档：`backend/api_doc.md`

---

**记住**：开发用 `local`，部署用 `production`！ 🚀
