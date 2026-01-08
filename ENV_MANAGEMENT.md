# 环境配置管理指南

本项目实现了本地开发环境和线上生产环境的自动切换工作流。

## 📁 配置文件说明

### 后端配置

- **`.env`** - 当前激活的环境配置（不提交到Git）
- **`.env.local`** - 本地开发环境模板（可提交）
  - 数据库：`localhost:3306`
  - API地址：`http://localhost:8000`
- **`.env.production`** - 生产环境模板（可提交）
  - 数据库：阿里云RDS
  - API地址：`https://surveyproduct.onrender.com`
- **`.env.example`** - 环境变量示例（可提交）

### 前端配置

- **`frontend/.env.development`** - 本地开发环境（Vite自动使用）
- **`frontend/.env.production`** - 生产环境（npm run build时使用）

## 🚀 快速开始

### 1. 首次设置

```bash
# 进入项目目录
cd survey_product_doc/SurveyProduct/survey_product_doc

# 安装 Git hooks
./scripts/setup-hooks.sh

# 切换到本地开发环境
./scripts/switch-env.sh local
```

### 2. 日常开发

#### 开发时（使用本地配置）

```bash
# 切换到本地环境
./scripts/switch-env.sh local

# 启动服务
# 后端
python -m uvicorn backend.app.main:app --reload

# 前端
cd frontend && npm run dev
```

#### 准备部署（切换到生产配置）

```bash
# 切换到生产环境
./scripts/switch-env.sh production

# 检查配置
cat .env | grep DATABASE_URL

# 提交代码
git add .
git commit -m "准备部署到生产环境"
git push origin main
```

#### 部署后（切回本地配置）

```bash
# 部署完成后，切回本地环境继续开发
./scripts/switch-env.sh local

# 提交切换记录
git add .env
git commit -m "切回本地开发环境"
```

## 🔄 自动化工作流

### Git Pre-commit Hook

在每次 `git commit` 之前，系统会自动：

1. ✅ 检查当前 `.env` 配置
2. ⚠️  如果是本地配置，提示是否要切换到生产环境
3. 🚦 询问是否继续提交

这样可以避免意外提交本地配置到生产环境。

### 工作流程图

```
开发阶段 (本地)
    ↓
./scripts/switch-env.sh local
    ↓
开发、测试
    ↓
准备部署
    ↓
./scripts/switch-env.sh production
    ↓
git commit (自动检查配置)
    ↓
git push
    ↓
Render 自动部署
    ↓
./scripts/switch-env.sh local (切回本地)
```

## 📝 命令参考

### 环境切换

```bash
# 切换到本地开发环境
./scripts/switch-env.sh local

# 切换到生产环境
./scripts/switch-env.sh production
# 或简写
./scripts/switch-env.sh prod
```

### Git Hooks管理

```bash
# 安装 Git hooks
./scripts/setup-hooks.sh

# 卸载 Git hooks（如果需要）
rm .git/hooks/pre-commit
```

### 查看当前配置

```bash
# 查看后端配置
cat .env

# 查看前端配置（开发环境）
cat frontend/.env.development

# 查看前端配置（生产环境）
cat frontend/.env.production
```

## 🔒 安全注意事项

### ✅ 可以提交的文件

- `.env.local` - 本地配置模板
- `.env.production` - 生产配置模板（如果不包含真实密码）
- `.env.example` - 示例文件

### ❌ 不应提交的文件

- `.env` - 当前激活的配置（已在 `.gitignore` 中）
- 任何包含真实密码、密钥的文件

### 🔐 敏感信息处理

如果 `.env.production` 包含真实的生产密码，建议：

1. **方案A**：不提交 `.env.production`，在Render环境变量中配置
2. **方案B**：使用环境变量占位符

```bash
# .env.production 使用占位符
DATABASE_URL="${DATABASE_URL}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY}"

# 在 Render 中配置实际值
```

## 🐛 故障排除

### 问题：切换环境后服务不生效

**解决**：重启服务

```bash
# 重启后端（如果使用 --reload 会自动重载）
# 或手动重启

# 重启前端
cd frontend
npm run dev
```

### 问题：Git hook 没有执行

**解决**：检查执行权限

```bash
# 查看权限
ls -la .git/hooks/pre-commit

# 添加执行权限
chmod +x .git/hooks/pre-commit
```

### 问题：.env.local 或 .env.production 不存在

**解决**：从模板创建

```bash
# 如果文件丢失，从当前 .env 创建
cp .env .env.local
# 或
cp .env .env.production

# 然后手动编辑配置
```

## 📚 最佳实践

### 1. 定期同步配置

确保 `.env.local` 和 `.env.production` 包含相同的配置项（但值不同）：

```bash
# 检查配置项
diff <(grep "^[A-Z]" .env.local | cut -d'=' -f1 | sort) \
     <(grep "^[A-Z]" .env.production | cut -d'=' -f1 | sort)
```

### 2. 提交前检查

```bash
# 查看即将提交的配置
cat .env | grep -E "DATABASE_URL|API_BASE_URL"
```

### 3. 使用别名简化操作

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias env-local='./scripts/switch-env.sh local'
alias env-prod='./scripts/switch-env.sh production'
```

## 🎯 总结

这个工作流帮助你：

✅ 轻松在本地和生产环境间切换  
✅ 避免意外提交错误配置  
✅ 自动化环境配置管理  
✅ 保护敏感信息安全  

**记住**：开发用 `local`，部署用 `production`！
