# GitHub部署指南

## 手动部署步骤

由于GitHub令牌认证问题，请按照以下步骤手动部署代码到GitHub：

### 步骤1：克隆仓库（如果尚未克隆）

```bash
git clone https://github.com/he2827987/SurveyProduct.git
cd SurveyProduct
```

### 步骤2：应用我们的更改

您需要应用我们刚才进行的所有更改。以下是主要修改的文件列表：

1. **requirements.txt** - 更新了数据库依赖
2. **config.py** - 更新了数据库URL格式
3. **.env.example** - 更新了示例连接字符串
4. **alembic.ini** - 更新了迁移工具的数据库URL
5. **render.yaml** - 更新了生产环境配置
6. **migrate_data.py** - 新增的数据迁移脚本
7. **alembic/versions/1a2b3c4d5e6f_postgresql_initial_migration.py** - 新增的Alembic迁移
8. **PostgreSQL_Migration_Guide.md** - 迁移指南文档

### 步骤3：提交并推送更改

1. 添加所有更改：
   ```bash
   git add .
   ```

2. 提交更改：
   ```bash
   git commit -m "feat: migrate database from MySQL to PostgreSQL for Render.com deployment

   - Replace PyMySQL with psycopg2-binary in requirements.txt
   - Update database URL format from MySQL to PostgreSQL
   - Create PostgreSQL-compatible database schema
   - Add data migration script for MySQL to PostgreSQL
   - Update Alembic migration files for PostgreSQL compatibility
   - Update render.yaml configuration for PostgreSQL deployment
   - Add comprehensive PostgreSQL migration guide

   This change enables the project to be deployed on Render.com with PostgreSQL database."
   ```

3. 推送到GitHub：
   ```bash
   git push origin main
   ```

   如果需要身份验证，请输入您的GitHub用户名和个人访问令牌。

### 步骤4：在Render.com上配置部署

1. **登录Render.com**：
   - 访问 [Render.com](https://render.com)
   - 使用GitHub账户登录

2. **创建PostgreSQL数据库**：
   - 点击 "New +"
   - 选择 "PostgreSQL"
   - 配置数据库实例（建议使用免费计划开始）
   - 记下数据库连接信息

3. **创建Web服务**：
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接到您的GitHub仓库
   - Render会自动检测Python项目
   - 配置以下环境变量：
     ```
     DATABASE_URL=postgresql://username:password@host:5432/database_name
     SECRET_KEY=your-secret-key-here
     OPENROUTER_API_KEY=your-openrouter-api-key
     ```

4. **部署设置**：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd survey_product_doc && python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### 步骤5：执行数据库迁移

1. **方法1：使用Render Shell（推荐）**：
   - 部署后，进入Render控制台
   - 打开Web服务的Shell
   - 运行迁移脚本：
     ```bash
     python migrate_data.py
     ```

2. **方法2：本地迁移**：
   - 在本地运行迁移脚本，将MySQL数据导出到PostgreSQL
   - 然后部署到Render

### 步骤6：验证部署

1. **检查日志**：
   - 在Render控制台查看部署日志
   - 确保没有错误

2. **测试API**：
   - 访问健康检查端点：`https://your-app-name.onrender.com/api/v1/health`
   - 测试其他API端点

3. **测试前端**：
   - 访问应用主页：`https://your-app-name.onrender.com`

## 故障排除

### 常见问题

1. **构建失败**：
   - 检查requirements.txt中的依赖版本
   - 查看构建日志中的错误信息

2. **数据库连接错误**：
   - 确认DATABASE_URL格式正确
   - 检查数据库是否正在运行
   - 验证用户权限

3. **迁移失败**：
   - 确保迁移脚本配置正确
   - 检查数据库权限
   - 查看错误日志

### 调试技巧

1. **查看详细日志**：
   ```bash
   # 在Render Shell中
   python -c "
   import os
   print(f'DATABASE_URL: {os.getenv(\"DATABASE_URL\")}')
   "
   ```

2. **测试数据库连接**：
   ```bash
   # 在Render Shell中
   python -c "
   from backend.app.database import engine
   try:
       with engine.connect() as conn:
           print('数据库连接成功')
   except Exception as e:
       print(f'数据库连接失败: {e}')
   "
   ```

## 自动部署设置

推送代码到GitHub后，Render会自动触发部署流程。您可以：

1. **设置自动部署**：
   - 在Render控制台
   - 进入Web服务设置
   - 启用 "Auto-Deploy" 选项

2. **配置部署钩子**：
   - 设置预部署和后部署钩子
   - 运行测试和迁移脚本

## 性能优化

1. **数据库优化**：
   - 配置连接池
   - 添加适当索引
   - 监控查询性能

2. **应用优化**：
   - 配置CDN
   - 启用压缩
   - 优化静态资源

---

完成这些步骤后，您的应用将成功运行在PostgreSQL数据库上，并部署在Render.com平台上。