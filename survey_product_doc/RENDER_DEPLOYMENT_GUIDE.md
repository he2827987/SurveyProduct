# Render 云端部署指南

## 📋 概述

本指南将帮助你将 SurveyProduct 项目部署到 Render 云端，并连接到外部 MySQL 数据库。

## 🎯 部署架构

```
┌─────────────────┐    ┌─────────────────┐
│   Render Web    │    │  External MySQL │
│   Service       │◄──►│   Database      │
│                 │    │                 │
│ - FastAPI App   │    │ - survey_db     │
│ - Python 3.11   │    │ - User Data     │
│ - Port $PORT    │    │ - Survey Data   │
└─────────────────┘    └─────────────────┘
```

## 🚀 部署步骤

### 1. 准备外部 MySQL 数据库

#### 选项 A: 使用云数据库服务
- **AWS RDS**: 创建 MySQL 实例
- **Google Cloud SQL**: 创建 MySQL 实例
- **Azure Database**: 创建 MySQL 实例
- **PlanetScale**: 无服务器 MySQL 平台
- **Railway**: 提供 MySQL 数据库服务

#### 选项 B: 使用 Render 的 PostgreSQL (推荐)
虽然项目使用 MySQL，但 Render 提供免费的 PostgreSQL 服务，我们可以稍作调整。

### 2. 在 Render 创建 Web 服务

#### 2.1 连接 GitHub 仓库
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New +" → "Web Service"
3. 选择 "Build and deploy from a Git repository"
4. 连接你的 GitHub 仓库

#### 2.2 配置服务设置
```
Name: survey-product-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (留空)
```

#### 2.3 构建和启动命令
```
Build Command:
cd survey_product_doc
pip install -r requirements.txt
python backend/init_database.py

Start Command:
cd survey_product_doc
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### 3. 配置环境变量

在 Render Dashboard 的 "Environment" 标签页中添加以下环境变量：

#### 3.1 数据库配置
```bash
# 方式1: 使用完整的数据库URL
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name

# 方式2: 使用单独的配置项
MYSQL_HOST=your-mysql-host.com
MYSQL_PORT=3306
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=survey_db
```

#### 3.2 应用配置
```bash
SECRET_KEY=your-super-secret-jwt-key-here
OPENROUTER_API_KEY=your-openrouter-api-key
ENVIRONMENT=production
```

### 4. 数据库初始化

#### 4.1 自动初始化
项目已配置在构建时自动运行数据库初始化脚本：
```python
python backend/init_database.py
```

#### 4.2 手动初始化 (如果需要)
如果自动初始化失败，可以通过 Render Shell 手动执行：
```bash
cd survey_product_doc
python backend/init_database.py
```

## 🔧 配置示例

### 使用 PlanetScale MySQL
```bash
DATABASE_URL=mysql+pymysql://username:password@aws.connect.psdb.cloud/survey_db?ssl-mode=REQUIRED
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
```

### 使用 Railway MySQL
```bash
MYSQL_HOST=containers-us-west-xxx.railway.app
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=railway
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
```

### 使用 AWS RDS
```bash
MYSQL_HOST=your-rds-endpoint.region.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=survey_db
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
```

## 📊 数据库表结构

项目会自动创建以下表：
- `organizations` - 组织信息
- `users` - 用户信息
- `departments` - 部门信息
- `participants` - 参与者信息
- `surveys` - 调研信息
- `questions` - 问题信息
- `survey_answers` - 调研答案
- `organization_members` - 组织成员关系
- `categories` - 问题分类
- `tags` - 问题标签

## 🔍 部署验证

### 1. 检查服务状态
访问 Render Dashboard，确认服务状态为 "Live"

### 2. 测试 API 端点
```bash
# 健康检查
curl https://your-app.onrender.com/api/v1/health

# API 文档
https://your-app.onrender.com/docs
```

### 3. 检查数据库连接
查看 Render 日志，确认数据库初始化成功：
```
✅ 数据库连接成功!
✅ 数据库表创建成功!
```

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败
**错误**: `Can't connect to MySQL server`
**解决方案**:
- 检查数据库主机地址和端口
- 确认数据库用户权限
- 检查防火墙设置
- 验证 SSL 配置

#### 2. 构建失败
**错误**: `Build failed`
**解决方案**:
- 检查 Python 版本兼容性
- 确认 requirements.txt 文件
- 查看构建日志中的具体错误

#### 3. 应用启动失败
**错误**: `Application failed to start`
**解决方案**:
- 检查环境变量配置
- 确认启动命令正确
- 查看应用日志

### 日志查看
1. 在 Render Dashboard 中选择你的服务
2. 点击 "Logs" 标签页
3. 查看实时日志和错误信息

## 🔒 安全配置

### 1. 环境变量安全
- 使用强密码和密钥
- 定期轮换密钥
- 不要在代码中硬编码敏感信息

### 2. 数据库安全
- 使用 SSL 连接
- 限制数据库访问 IP
- 定期备份数据

### 3. API 安全
- 启用 HTTPS
- 配置 CORS 策略
- 使用 JWT 认证

## 📈 性能优化

### 1. 数据库优化
- 创建适当的索引
- 使用连接池
- 定期清理旧数据

### 2. 应用优化
- 启用缓存
- 优化数据库查询
- 使用 CDN 加速静态资源

## 🔄 持续部署

### 自动部署
- 推送到 main 分支自动触发部署
- 使用 GitHub Actions 进行额外测试
- 配置部署通知

### 回滚策略
- 保留多个部署版本
- 快速回滚到稳定版本
- 监控部署成功率

## 📞 支持

如果遇到问题：
1. 查看 Render 文档
2. 检查项目日志
3. 验证环境变量配置
4. 联系技术支持

---

## 🎉 部署完成

部署成功后，你将获得：
- ✅ 云端运行的 FastAPI 应用
- ✅ 连接外部 MySQL 数据库
- ✅ 自动数据库初始化
- ✅ HTTPS 安全连接
- ✅ 自动扩缩容
- ✅ 监控和日志

你的 SurveyProduct 应用现在已经在云端运行了！
