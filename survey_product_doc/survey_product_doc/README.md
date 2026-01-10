# 调研产品文档系统

一个基于FastAPI和Vue.js的现代化调研管理系统，支持问卷创建、数据收集、分析和可视化。

## 🚀 快速开始

### 系统要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 自动安装依赖

#### macOS/Linux
```bash
./install_dependencies.sh
```

#### Windows
```cmd
install_dependencies.bat
```

### 手动安装依赖

#### 1. 后端依赖安装

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat  # Windows

# 安装Python依赖
pip install -r requirements.txt
```

#### 2. 前端依赖安装

```bash
cd frontend
npm install
```

## 📦 项目依赖

### 后端依赖

#### 核心框架
- **FastAPI** (0.115.14) - 现代、快速的Web框架
- **Uvicorn** (0.35.0) - ASGI服务器
- **Starlette** (0.46.2) - ASGI框架

#### 数据库
- **SQLAlchemy** (2.0.41) - ORM框架
- **PyMySQL** (1.1.1) - MySQL连接器
- **Alembic** (1.16.3) - 数据库迁移工具

#### 数据验证
- **Pydantic** (2.11.7) - 数据验证和序列化
- **Pydantic-settings** (2.10.1) - 配置管理

#### 认证和安全
- **Python-jose** (3.5.0) - JWT处理
- **Passlib** (1.7.4) - 密码哈希
- **Bcrypt** (4.3.0) - 密码加密
- **Python-multipart** (0.0.20) - 表单处理

#### HTTP客户端
- **HTTPX** (0.28.1) - 异步HTTP客户端
- **Requests** (2.32.4) - HTTP库

#### 工具库
- **Python-dotenv** (1.1.1) - 环境变量管理
- **Email-validator** (2.2.0) - 邮箱验证
- **QRCode** (8.2) - 二维码生成
- **Pillow** (11.3.0) - 图像处理

### 前端依赖

#### 核心框架
- **Vue.js** (3.5.20) - 渐进式JavaScript框架
- **Vue Router** (4.2.5) - 官方路由管理器

#### UI组件库
- **Element Plus** (2.11.1) - Vue 3组件库

#### 工具库
- **Axios** (1.6.7) - HTTP客户端
- **ECharts** (5.6.0) - 数据可视化
- **Vue-ECharts** (7.0.3) - Vue ECharts组件
- **QRCode** (1.5.4) - 二维码生成
- **HTML2Canvas** (1.4.1) - 页面截图

#### 开发工具
- **Vite** (5.4.19) - 构建工具
- **@vitejs/plugin-vue** (5.2.4) - Vue插件

## 🏃‍♂️ 启动服务

### 1. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

### 3. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🔧 配置

### 环境变量

创建 `.env` 文件在 `backend` 目录下：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/survey_db

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter API配置
OPENROUTER_API_KEY=your-openrouter-api-key
DEFAULT_MODEL=mistralai/mistral-7b-instruct:free
```

### 数据库配置

1. 创建MySQL数据库：
```sql
CREATE DATABASE survey_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 运行数据库迁移：
```bash
cd backend
alembic upgrade head
```

## 📁 项目结构

```
survey_product_doc/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # 数据验证模式
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面组件
│   │   └── router/        # 路由配置
│   └── package.json       # Node.js依赖
├── requirements.txt        # 项目依赖
├── install_dependencies.sh # 安装脚本(Linux/macOS)
└── install_dependencies.bat # 安装脚本(Windows)
```

## 🎯 主要功能

### 调研管理
- ✅ 创建和编辑调研问卷
- ✅ 题目库管理
- ✅ 调研发布和状态管理
- ✅ 二维码生成

### 数据收集
- ✅ 移动端调研填写
- ✅ 数据实时收集
- ✅ 参与者管理

### 数据分析
- ✅ 数据可视化图表
- ✅ AI智能分析
- ✅ 企业对比分析
- ✅ 数据导出

### 用户管理
- ✅ 用户注册和登录
- ✅ 组织管理
- ✅ 权限控制

## 🔒 安全特性

- JWT身份认证
- 密码加密存储
- 权限控制
- 数据验证
- CORS配置

## 🚀 部署

### 生产环境部署

1. 构建前端：
```bash
cd frontend
npm run build
```

2. 配置生产环境变量

3. 使用生产级服务器（如Gunicorn）

4. 配置反向代理（如Nginx）

## 📝 开发指南

### 代码规范
- 使用Black进行Python代码格式化
- 使用ESLint进行JavaScript代码检查
- 遵循PEP 8和Vue.js风格指南

### 测试
- 后端API测试
- 前端组件测试
- 集成测试

### 贡献
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License

## 🤝 支持

如有问题或建议，请提交Issue或联系开发团队。
