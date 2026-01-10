# 🚀 快速开始指南

## 环境配置工作流

### 📦 一次性设置（首次使用）

```bash
# 1. 进入项目目录
cd survey_product_doc/SurveyProduct/survey_product_doc

# 2. 安装 Git hooks
./scripts/setup-hooks.sh

# 3. 切换到本地开发环境
make local
# 或
./scripts/switch-env.sh local

# 4. 安装依赖（如果还没有）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 🔄 日常开发工作流

#### 方式1：使用Make命令（推荐）

```bash
# 切换到本地环境
make local

# 查看当前配置
make status

# 启动服务（需要两个终端）
# 终端1：
make start-backend

# 终端2：
cd frontend && npm run dev
```

#### 方式2：使用脚本

```bash
# 切换到本地环境
./scripts/switch-env.sh local

# 启动服务...
```

### 🚢 部署到生产环境

```bash
# 1. 切换到生产配置
make prod
# 或
./scripts/switch-env.sh production

# 2. 检查配置是否正确
make check-prod
# 或
./scripts/deploy-check.sh

# 3. 提交代码
git add .
git commit -m "feat: 新功能"
# ⚠️ 会自动检查配置

# 4. 推送到远程
git push origin main

# 5. 部署完成后，切回本地环境
make local
```

## 📋 命令速查表

| 命令 | 说明 |
|------|------|
| `make local` | 切换到本地环境 |
| `make prod` | 切换到生产环境 |
| `make status` | 查看当前配置 |
| `make check-prod` | 检查生产配置 |
| `./scripts/switch-env.sh local` | 切换到本地（脚本方式） |
| `./scripts/switch-env.sh production` | 切换到生产（脚本方式） |

## 🎯 典型场景

### 场景1：早上开始开发

```bash
cd survey_product_doc/SurveyProduct/survey_product_doc
make local
make status  # 确认是本地配置

# 启动服务...
```

### 场景2：下午准备部署

```bash
# 开发完成
git status

# 切换到生产
make prod

# 检查配置
make check-prod

# 提交推送
git add .
git commit -m "feat: 完成XXX功能"
git push

# 切回本地
make local
```

### 场景3：紧急修复

```bash
# 快速切换
make prod

# 修复提交
git add .
git commit -m "fix: 紧急修复XXX"
git push

# 切回
make local
```

## ⚠️ 注意事项

1. **始终在本地环境开发**
   - 使用 `make local` 确保配置正确
   
2. **部署前检查配置**
   - 运行 `make check-prod` 验证
   
3. **部署后切回本地**
   - 避免意外使用生产数据库

4. **Git commit 会自动检查**
   - 如果是本地配置会提示
   - 可以选择继续或取消

## 🔍 故障排除

### 问题：make 命令不存在

**解决**：直接使用脚本

```bash
./scripts/switch-env.sh local
```

### 问题：权限被拒绝

**解决**：添加执行权限

```bash
chmod +x scripts/*.sh
```

### 问题：环境没有切换

**解决**：检查文件是否存在

```bash
ls -la .env*
cat .env
```

## 📚 更多信息

- 详细文档：`ENV_MANAGEMENT.md`
- 工作流说明：`WORKFLOW_README.md`
- 项目文档：`README.md`

---

**快速开始**: `make local` → 开发 → `make prod` → 部署 → `make local` 🔄
