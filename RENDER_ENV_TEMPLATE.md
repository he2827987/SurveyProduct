# Render 环境变量配置模板

## 📋 必需的环境变量

在 Render Dashboard 的 "Environment" 标签页中添加以下环境变量：

### 1. 数据库配置 (选择其中一种方式)

#### 方式 A: 使用完整的数据库 URL
```bash
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
```

#### 方式 B: 使用单独的配置项 (推荐)
```bash
MYSQL_HOST=your-mysql-host.com
MYSQL_PORT=3306
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=survey_db
```

### 2. 应用安全配置
```bash
SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
```

### 3. AI 功能配置
```bash
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 4. 环境标识
```bash
ENVIRONMENT=production
```

## 🔧 不同数据库服务商的配置示例

### PlanetScale MySQL
```bash
DATABASE_URL=mysql+pymysql://username:password@aws.connect.psdb.cloud/survey_db?ssl-mode=REQUIRED
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
ENVIRONMENT=production
```

### Railway MySQL
```bash
MYSQL_HOST=containers-us-west-xxx.railway.app
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=railway
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
ENVIRONMENT=production
```

### AWS RDS MySQL
```bash
MYSQL_HOST=your-rds-endpoint.region.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=survey_db
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
ENVIRONMENT=production
```

### Google Cloud SQL
```bash
MYSQL_HOST=your-instance-ip
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=survey_db
SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-openrouter-key
ENVIRONMENT=production
```

## 🔒 安全建议

### 1. 密钥生成
使用以下命令生成强密钥：
```bash
# 生成随机密钥
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. 密码要求
- 至少 16 个字符
- 包含大小写字母、数字和特殊字符
- 避免使用常见密码

### 3. 环境变量保护
- 不要在代码中硬编码敏感信息
- 使用 Render 的环境变量功能
- 定期轮换密钥和密码

## 📝 配置步骤

1. **登录 Render Dashboard**
   - 访问 https://dashboard.render.com
   - 选择你的 Web 服务

2. **进入环境变量设置**
   - 点击 "Environment" 标签页
   - 点击 "Add Environment Variable"

3. **添加变量**
   - 输入变量名和值
   - 点击 "Save Changes"

4. **重新部署**
   - 环境变量更改后需要重新部署
   - 点击 "Manual Deploy" → "Deploy latest commit"

## ✅ 验证配置

部署完成后，检查以下内容：

1. **健康检查**
   ```bash
   curl https://your-app.onrender.com/api/v1/health
   ```

2. **API 文档**
   - 访问 https://your-app.onrender.com/docs
   - 确认 API 文档正常显示

3. **数据库连接**
   - 查看 Render 日志
   - 确认数据库初始化成功

## 🚨 常见问题

### 数据库连接失败
- 检查主机地址和端口
- 确认用户名和密码正确
- 验证数据库服务是否运行

### 应用启动失败
- 检查所有必需的环境变量
- 确认 SECRET_KEY 已设置
- 查看应用启动日志

### API 功能异常
- 确认 OPENROUTER_API_KEY 有效
- 检查数据库表是否正确创建
- 验证环境变量格式

---

**注意**: 请根据你选择的数据库服务商，使用相应的配置示例。确保所有敏感信息都通过环境变量设置，不要提交到代码仓库中。
