# PostgreSQL数据库部署完成指南

## 数据库连接信息（已更新）

- **数据库名称**: `surveyproduct_db`
- **用户名**: `surveyproduct_db_user`
- **密码**: `1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD`
- **主机**: `dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com`
- **端口**: `5432`
- **SSL模式**: `require`
- **完整URL**: `postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com:5432/surveyproduct_db?sslmode=require`

## 已完成的工作

### 1. 数据库配置更新
- ✅ 更新了 `render.yaml` 中的数据库URL
- ✅ 更新了 `.env.example` 中的示例连接字符串
- ✅ 更新了 `backend/app/config.py` 中的数据库URL
- ✅ 更新了 `alembic.ini` 中的数据库URL
- ✅ 更新了 `migrate_data.py` 中的数据库连接配置

### 2. 添加了SSL配置
- ✅ 所有数据库连接都添加了 `sslmode=require`
- ✅ 确保连接安全性

### 3. 创建了数据库脚本
- ✅ `postgresql_schema.sql` - 完整的PostgreSQL表结构
- ✅ `create_basic_tables_ssl.py` - 创建基本表结构的Python脚本
- ✅ `migrate_data.py` - 数据迁移脚本

## Render.com部署步骤

### 1. 推送代码到GitHub
```bash
git add .
git commit -m "config: add SSL configuration to PostgreSQL connection"
git push origin main
```

### 2. 在Render.com上部署
1. **登录Render.com**并连接到您的GitHub仓库
2. **设置环境变量**：
   ```
   DATABASE_URL=postgresql://surveyproduct_db_user:1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD@dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com:5432/surveyproduct_db?sslmode=require
   SECRET_KEY=your-secret-key-here
   OPENROUTER_API_KEY=your-openrouter-api-key
   ```

3. **配置构建命令**：
   ```
   pip install -r requirements.txt
   ```

4. **配置启动命令**：
   ```
   cd survey_product_doc && python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```

### 3. 数据库初始化选项

#### 选项A：使用Alembic自动迁移（推荐）
- Render部署时会自动运行 `python -m alembic upgrade head`
- 这会创建所有必要的表结构

#### 选项B：手动运行初始化脚本
1. 部署后，进入Render Shell
2. 运行基本表创建脚本：
   ```bash
   python create_basic_tables_ssl.py
   ```

#### 选项C：从MySQL迁移数据
1. 如果需要从现有MySQL数据库迁移数据
2. 运行数据迁移脚本：
   ```bash
   python migrate_data.py
   ```

## 验证部署

### 1. 检查应用状态
访问健康检查端点：
```
https://your-app-name.onrender.com/api/v1/health
```

### 2. 检查数据库连接
在Render Shell中运行：
```bash
python -c "
from backend.app.database import engine
try:
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
"
```

### 3. 检查表结构
在Render Shell中运行：
```bash
python -c "
from backend.app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\''))
    tables = [row[0] for row in result.fetchall()]
    print(f'数据库表: {tables}')
"
```

## 常见问题解决

### 1. SSL连接错误
确保所有数据库连接都包含 `sslmode=require` 参数

### 2. 数据库连接超时
检查网络连接和防火墙设置

### 3. 表创建失败
- 检查数据库权限
- 确保SQL语法正确
- 查看错误日志

## 后续维护

1. **定期备份**：在Render控制台设置自动备份
2. **监控性能**：使用Render的监控工具
3. **更新依赖**：定期更新PostgreSQL和Python依赖

---

现在您的PostgreSQL数据库已完全配置好，并可以在Render.com上成功部署！所有必要的配置文件已更新，连接信息已正确设置，SSL配置已添加。