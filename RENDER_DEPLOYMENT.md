# Render 部署指南

## 概述

本指南将帮助你在 Render 上部署 SurveyProduct 应用。

## 部署步骤

### 1. 创建数据库服务

1. 在 Render Dashboard 中，点击 "New +" → "PostgreSQL" 或 "MySQL"
2. 选择 "MySQL" 服务
3. 配置数据库：
   - **Name**: `survey-product-db`
   - **Database**: `survey_db`
   - **User**: `survey_user`
   - **Password**: 生成一个强密码
   - **Plan**: Free

### 2. 创建 Web 服务

1. 在 Render Dashboard 中，点击 "New +" → "Web Service"
2. 连接你的 GitHub 仓库
3. 配置服务：
   - **Name**: `survey-product-backend`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     cd survey_product_doc
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd survey_product_doc
     python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```

### 3. 配置环境变量

在 Web 服务的 "Environment" 标签页中添加以下环境变量：

#### 必需的环境变量

- **DATABASE_URL**: 
  ```
  mysql+pymysql://survey_user:YOUR_PASSWORD@YOUR_DB_HOST:3306/survey_db
  ```
  > 从数据库服务的 "Info" 标签页获取连接信息

- **SECRET_KEY**: 
  ```
  your-super-secret-jwt-key-here
  ```

- **OPENROUTER_API_KEY**: 
  ```
  your-openrouter-api-key
  ```

#### 可选的环境变量

- **MYSQL_HOST**: 数据库主机地址
- **MYSQL_PORT**: 数据库端口 (默认: 3306)
- **MYSQL_USER**: 数据库用户名
- **MYSQL_PASSWORD**: 数据库密码
- **MYSQL_DATABASE**: 数据库名称

### 4. 数据库迁移

部署完成后，需要运行数据库迁移：

1. 在 Render Dashboard 中，进入你的 Web 服务
2. 点击 "Shell" 标签页
3. 运行以下命令：
   ```bash
   cd survey_product_doc
   alembic upgrade head
   ```

### 5. 验证部署

1. 访问你的 Web 服务 URL
2. 检查 API 文档：`https://your-app.onrender.com/docs`
3. 测试数据库连接

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 环境变量是否正确
   - 确保数据库服务已启动
   - 验证网络连接

2. **构建失败**
   - 检查 `requirements.txt` 文件
   - 确保 Python 版本兼容
   - 查看构建日志

3. **应用启动失败**
   - 检查启动命令是否正确
   - 验证环境变量配置
   - 查看应用日志

### 日志查看

在 Render Dashboard 中：
1. 选择你的服务
2. 点击 "Logs" 标签页
3. 查看实时日志

## 环境变量说明

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接字符串 | `mysql+pymysql://user:pass@host:3306/db` |
| SECRET_KEY | JWT 密钥 | `your-secret-key` |
| OPENROUTER_API_KEY | OpenRouter API 密钥 | `sk-or-v1-...` |
| MYSQL_HOST | MySQL 主机 | `dpg-xxx.oregon-postgres.render.com` |
| MYSQL_PORT | MySQL 端口 | `3306` |
| MYSQL_USER | MySQL 用户名 | `survey_user` |
| MYSQL_PASSWORD | MySQL 密码 | `your-password` |
| MYSQL_DATABASE | MySQL 数据库名 | `survey_db` |

## 注意事项

1. **免费计划限制**：
   - 服务在 15 分钟无活动后会自动休眠
   - 首次访问可能需要几秒钟来唤醒服务

2. **数据库连接**：
   - 确保数据库服务在 Web 服务之前创建
   - 使用内部连接字符串以获得最佳性能

3. **安全性**：
   - 不要在代码中硬编码敏感信息
   - 使用环境变量存储所有配置

## 支持

如果遇到问题，请：
1. 查看 Render 文档
2. 检查应用日志
3. 验证环境变量配置
4. 联系技术支持
