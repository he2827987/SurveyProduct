# PostgreSQL数据库部署指南

## 数据库连接信息

- **数据库名称**: `surveyproduct_db`
- **用户名**: `surveyproduct_db_user`
- **密码**: `1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD`
- **主机**: `dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com`
- **外部连接URL**: `postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a/surveyproduct_db`
- **PSQL命令**: `PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD psql -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db`

## 部署步骤

### 方法1: 使用Alembic自动迁移（推荐）

1. **提交并推送代码更改**：
   ```bash
   git add .
   git commit -m "config: update database URLs for PostgreSQL deployment"
   git push origin main
   ```

2. **在Render.com上部署**：
   - Render会自动使用`render.yaml`中的配置
   - 数据库会通过Alembic自动创建表结构

### 方法2: 手动数据库初始化

如果您想手动设置数据库：

1. **连接到数据库**：
   ```bash
   PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD psql -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db
   ```

2. **执行SQL脚本**：
   ```sql
   -- 执行SurveyPostgreSQL_schema.sql中的内容
   -- 或者运行Alembic迁移
   ```

3. **运行Alembic迁移**：
   ```bash
   # 设置环境变量
   export DATABASE_URL="postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a/surveyproduct_db"
   
   # 运行迁移
   python -m alembic upgrade head
   ```

### 方法3: 从MySQL迁移数据（如果需要保留现有数据）

1. **准备MySQL数据库**：
   - 确保MySQL数据库可以访问
   - 更新`migrate_data.py`中的MySQL连接配置

2. **运行迁移脚本**：
   ```bash
   python migrate_data.py
   ```

## Render.com部署配置

确保您的Render.com Web服务具有以下配置：

### 环境变量
```
DATABASE_URL=postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a/surveyproduct_db
SECRET_KEY=your-secret-key-here
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 启动命令
```
cd survey_product_doc && python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

## 验证部署

### 1. 检查数据库连接
```bash
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a/surveyproduct_db'
from backend.app.database import engine
try:
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
"
```

### 2. 检查表结构
```bash
PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD psql -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db -c "\dt"
```

### 3. 检查API健康状态
部署后访问：
```
https://your-app-name.onrender.com/api/v1/health
```

## 故障排除

### 常见问题

1. **连接超时**：
   - 检查防火墙设置
   - 确认数据库URL格式正确

2. **认证失败**：
   - 验证用户名和密码
   - 检查数据库权限

3. **表创建失败**：
   - 确保数据库有足够权限
   - 检查SQL语法

### 调试命令

1. **测试连接**：
   ```bash
   PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD psql -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db -c "SELECT version();"
   ```

2. **查看当前迁移状态**：
   ```bash
   export DATABASE_URL="postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a/surveyproduct_db"
   python -m alembic current
   ```

3. **查看迁移历史**：
   ```bash
   python -m alembic history
   ```

## 数据库管理

### 备份数据库
```bash
PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD pg_dump -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db > backup.sql
```

### 恢复数据库
```bash
PGPASSWORD=1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD psql -h dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com -U surveyproduct_db_user surveyproduct_db < backup.sql
```

---

完成这些步骤后，您的PostgreSQL数据库将正确配置并准备就绪，您的应用程序将能够在Render.com上成功运行！