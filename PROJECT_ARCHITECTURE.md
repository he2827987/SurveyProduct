# SurveyProduct 项目架构文档

## 📋 目录
- [项目概述](#项目概述)
- [目录结构](#目录结构)
- [技术栈](#技术栈)
- [数据库结构](#数据库结构)
- [模块划分](#模块划分)
- [API接口](#api接口)
- [启动方式](#启动方式)
- [部署流程](#部署流程)

---

## 项目概述

SurveyProduct 是一个基于 FastAPI + Vue.js 的企业级调研问卷系统，支持问卷设计、数据收集、智能分析和报告生成。

### 核心功能
- 👤 **用户管理**: 用户注册、登录、权限管理
- 🏢 **组织管理**: 多组织支持、组织成员管理
- 📝 **问卷管理**: 问卷创建、编辑、发布
- 📊 **题库管理**: 全局题库、组织题库、题目分类
- 📱 **数据收集**: 问卷填写、进度保存、提交管理
- 📈 **数据分析**: 统计分析、图表展示、AI总结
- 🔍 **企业对比**: 跨组织数据对比分析

---

## 目录结构

```
survey_product_doc/SurveyProduct/
├── survey_product_doc/                # 主项目目录
│   ├── backend/                       # 后端代码
│   │   ├── app/
│   │   │   ├── api/                   # API路由
│   │   │   │   ├── analysis_api.py    # 数据分析API
│   │   │   │   ├── analytics_api.py   # 统计分析API
│   │   │   │   ├── answer_api.py      # 答案API
│   │   │   │   ├── category_api.py    # 分类API
│   │   │   │   ├── department_api.py  # 部门API
│   │   │   │   ├── llm_api.py         # LLM智能分析API
│   │   │   │   ├── org_api.py         # 组织API
│   │   │   │   ├── participant_api.py # 参与者API
│   │   │   │   ├── question_api.py    # 题目API
│   │   │   │   ├── survey_api.py      # 问卷API
│   │   │   │   ├── tag_api.py         # 标签API
│   │   │   │   └── user_api.py        # 用户API
│   │   │   ├── models/                # 数据库模型
│   │   │   │   ├── answer.py          # 答案模型
│   │   │   │   ├── category.py        # 分类模型
│   │   │   │   ├── department.py      # 部门模型
│   │   │   │   ├── organization.py    # 组织模型
│   │   │   │   ├── participant.py     # 参与者模型
│   │   │   │   ├── question.py        # 题目模型
│   │   │   │   ├── survey.py          # 问卷模型
│   │   │   │   ├── tag.py             # 标签模型
│   │   │   │   └── user.py            # 用户模型
│   │   │   ├── schemas/               # Pydantic数据验证模型
│   │   │   ├── services/              # 业务逻辑服务
│   │   │   │   ├── chart_service.py   # 图表服务
│   │   │   │   ├── grading_service.py # 评分服务
│   │   │   │   ├── llm_service.py     # LLM服务
│   │   │   │   ├── statistics_service.py # 统计服务
│   │   │   │   ├── survey_service.py  # 问卷服务
│   │   │   │   └── user_service.py    # 用户服务
│   │   │   ├── config.py              # 配置文件
│   │   │   ├── crud.py                # 数据库CRUD操作
│   │   │   ├── database.py            # 数据库连接
│   │   │   ├── main.py                # 应用入口
│   │   │   └── security.py            # 安全认证
│   │   └── create_tags_table.sql      # SQL脚本
│   ├── frontend/                      # 前端代码
│   │   ├── src/
│   │   │   ├── api/                   # API调用封装
│   │   │   │   ├── analytics.js       # 分析API
│   │   │   │   ├── answer.js          # 答案API
│   │   │   │   ├── llm.js             # LLM API
│   │   │   │   ├── organization.js    # 组织API
│   │   │   │   ├── question.js        # 题目API
│   │   │   │   ├── survey.js          # 问卷API
│   │   │   │   └── user.js            # 用户API
│   │   │   ├── components/            # Vue组件
│   │   │   │   ├── AnalysisChart.vue  # 分析图表
│   │   │   │   ├── Layout.vue         # 布局组件
│   │   │   │   └── QRCodeGenerator.vue # 二维码生成器
│   │   │   ├── views/                 # 页面视图
│   │   │   │   ├── analysis/          # 数据分析页面
│   │   │   │   ├── compare/           # 企业对比页面
│   │   │   │   ├── organization/      # 组织管理页面
│   │   │   │   ├── question/          # 题库管理页面
│   │   │   │   └── survey/            # 问卷管理页面
│   │   │   ├── router/                # 路由配置
│   │   │   └── main.js                # 应用入口
│   │   ├── package.json               # 依赖配置
│   │   └── vite.config.js             # Vite配置
│   ├── alembic/                       # 数据库迁移
│   │   └── versions/                  # 迁移版本
│   ├── scripts/                       # 脚本工具
│   │   ├── switch-env.sh              # 环境切换
│   │   ├── deploy-check.sh            # 部署检查
│   │   └── setup-hooks.sh             # Git hooks设置
│   ├── tests/                         # 测试文件
│   ├── .env.local                     # 本地环境配置
│   ├── .env.production                # 生产环境配置
│   ├── alembic.ini                    # Alembic配置
│   └── requirements.txt               # Python依赖
├── render.yaml                        # Render部署配置
├── deploy_to_render.sh                # 部署脚本
├── DEPLOYMENT_SUMMARY.md              # 部署总结
├── ENV_MANAGEMENT.md                  # 环境管理文档
├── RENDER_DEPLOYMENT_GUIDE.md         # Render部署指南
└── README.md                          # 项目说明
```

---

## 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11.9 | 编程语言 |
| FastAPI | 0.115.14 | Web框架 |
| SQLAlchemy | 2.0.41 | ORM框架 |
| Alembic | 1.16.3 | 数据库迁移 |
| PyMySQL | 1.1.1 | MySQL驱动 |
| Pydantic | 2.11.7 | 数据验证 |
| Python-Jose | 3.5.0 | JWT认证 |
| Passlib | 1.7.4 | 密码加密 |
| Uvicorn | 0.35.0 | ASGI服务器 |
| HTTPX | 0.28.1 | HTTP客户端 |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.5.20 | 前端框架 |
| Vue Router | 4.2.5 | 路由管理 |
| Element Plus | 2.11.1 | UI组件库 |
| ECharts | 5.6.0 | 图表库 |
| Axios | 1.6.7 | HTTP客户端 |
| Vite | 5.4.19 | 构建工具 |

### 数据库
| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0 | 关系型数据库 |
| 阿里云RDS | - | 云数据库服务 |

### 外部服务
| 服务 | 用途 |
|------|------|
| OpenRouter | LLM智能分析服务 |
| Render | 云端部署平台 |
| GitHub | 代码托管 |

---

## 数据库结构

### 核心表结构

#### 1. users - 用户表
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'researcher', 'participant') DEFAULT 'researcher',
    is_active BOOLEAN DEFAULT TRUE,
    manager_id INT,
    organization_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**字段说明**:
- `username`: 用户名
- `email`: 邮箱
- `hashed_password`: 加密密码
- `role`: 角色（管理员/研究员/参与者）
- `is_active`: 账户状态
- `manager_id`: 上级管理者ID
- `organization_id`: 所属组织ID

#### 2. organizations - 组织表
```sql
CREATE TABLE organizations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

**字段说明**:
- `name`: 组织名称
- `description`: 组织描述
- `owner_id`: 组织创建者ID

#### 3. organization_members - 组织成员表
```sql
CREATE TABLE organization_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    organization_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('owner', 'admin', 'member') DEFAULT 'member',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_member (organization_id, user_id)
);
```

**字段说明**:
- `organization_id`: 组织ID
- `user_id`: 用户ID
- `role`: 成员角色（所有者/管理员/成员）

#### 4. surveys - 问卷表
```sql
CREATE TABLE surveys (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by_user_id INT NOT NULL,
    organization_id INT,
    status ENUM('draft', 'active', 'closed') DEFAULT 'draft',
    start_time DATETIME,
    end_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**字段说明**:
- `title`: 问卷标题
- `description`: 问卷描述
- `created_by_user_id`: 创建者ID
- `organization_id`: 所属组织ID
- `status`: 状态（草稿/进行中/已关闭）
- `start_time`: 开始时间
- `end_time`: 结束时间

#### 5. questions - 题目表
```sql
CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL,
    type ENUM('single_choice', 'multi_choice', 'text_input', 'number_input', 'sort_order', 'conditional') NOT NULL,
    options TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    `order` INT DEFAULT 0,
    owner_id INT,
    organization_id INT,
    category_id INT,
    usage_count INT DEFAULT 0,
    min_score INT DEFAULT 0,
    max_score INT DEFAULT 10,
    parent_question_id INT,
    trigger_options TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (parent_question_id) REFERENCES questions(id)
);
```

**字段说明**:
- `text`: 题目文本
- `type`: 题目类型（单选/多选/文本/数字/排序/关联）
- `options`: 选项（JSON格式）
- `is_required`: 是否必填
- `order`: 排序
- `owner_id`: 创建者ID
- `organization_id`: 所属组织ID
- `category_id`: 分类ID
- `usage_count`: 使用次数
- `min_score/max_score`: 分值范围
- `parent_question_id`: 父题目ID（关联题）
- `trigger_options`: 触发条件（JSON格式）

#### 6. survey_questions - 问卷题目关联表
```sql
CREATE TABLE survey_questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    survey_id INT NOT NULL,
    question_id INT NOT NULL,
    `order` INT DEFAULT 0,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_survey_question (survey_id, question_id)
);
```

**字段说明**:
- `survey_id`: 问卷ID
- `question_id`: 题目ID
- `order`: 题目在问卷中的排序

#### 7. survey_answers - 问卷答案表
```sql
CREATE TABLE survey_answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    survey_id INT NOT NULL,
    question_id INT NOT NULL,
    participant_id INT,
    answer_text TEXT,
    selected_options TEXT,
    score INT,
    total_score DECIMAL(10,2),
    department VARCHAR(255),
    position VARCHAR(255),
    organization_id INT,
    organization_name VARCHAR(255),
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (participant_id) REFERENCES participants(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**字段说明**:
- `survey_id`: 问卷ID
- `question_id`: 题目ID
- `participant_id`: 参与者ID
- `answer_text`: 文本答案
- `selected_options`: 选择的选项（JSON格式）
- `score`: 单题得分
- `total_score`: 总分
- `department`: 部门
- `position`: 职位
- `organization_id`: 组织ID
- `organization_name`: 组织名称

#### 8. departments - 部门表
```sql
CREATE TABLE departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    organization_id INT NOT NULL,
    parent_department_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (parent_department_id) REFERENCES departments(id)
);
```

#### 9. participants - 参与者表
```sql
CREATE TABLE participants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    department_id INT,
    organization_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

#### 10. categories - 题目分类表
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    parent_id INT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);
```

#### 11. tags - 标签表
```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 12. question_tags - 题目标签关联表
```sql
CREATE TABLE question_tags (
    question_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (question_id, tag_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### 数据库关系图

```
users (用户)
  ├── 1:N → surveys (创建的问卷)
  ├── 1:N → questions (创建的题目)
  ├── 1:N → organizations (创建的组织)
  ├── N:M → organizations (组织成员，通过organization_members)
  └── 1:N → users (下属员工，通过manager_id)

organizations (组织)
  ├── 1:N → surveys (组织的问卷)
  ├── 1:N → questions (组织题库)
  ├── 1:N → departments (组织部门)
  ├── 1:N → participants (组织参与者)
  └── N:M → users (组织成员，通过organization_members)

surveys (问卷)
  ├── N:M → questions (问卷题目，通过survey_questions)
  └── 1:N → survey_answers (问卷答案)

questions (题目)
  ├── N:M → surveys (所属问卷，通过survey_questions)
  ├── N:M → tags (题目标签，通过question_tags)
  ├── N:1 → categories (所属分类)
  ├── 1:N → survey_answers (题目答案)
  └── 1:N → questions (子题目，关联题)

categories (分类)
  ├── 1:N → questions (分类下的题目)
  └── 1:N → categories (子分类)

departments (部门)
  ├── 1:N → participants (部门参与者)
  └── 1:N → departments (子部门)
```

---

## 模块划分

### 1. 用户认证模块 (Authentication Module)

**位置**: `backend/app/security.py`, `backend/app/api/user_api.py`

**核心函数**:
```python
# security.py
def verify_password(plain_password: str, hashed_password: str) -> bool
def get_password_hash(password: str) -> str
def create_access_token(data: dict) -> str
def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User

# user_api.py
@router.post("/login/access-token")
def login_access_token(form_data: OAuth2PasswordRequestForm)

@router.post("/register")
def register_user(user: schemas.UserCreate)

@router.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user))
```

**数据流**:
1. 用户提交登录信息
2. 验证密码哈希
3. 生成JWT token
4. 返回access_token
5. 后续请求携带token验证身份

---

### 2. 问卷管理模块 (Survey Management Module)

**位置**: `backend/app/api/survey_api.py`, `backend/app/services/survey_service.py`

**核心函数**:
```python
# survey_api.py
@router.post("/surveys/", response_model=schemas.SurveyResponse)
def create_survey(survey: schemas.SurveyCreate, current_user: models.User)

@router.get("/surveys/", response_model=List[schemas.SurveyResponse])
def read_surveys(skip: int = 0, limit: int = 100)

@router.get("/surveys/{survey_id}", response_model=schemas.SurveyResponse)
def read_survey(survey_id: int)

@router.put("/surveys/{survey_id}", response_model=schemas.SurveyResponse)
def update_survey(survey_id: int, survey: schemas.SurveyUpdate)

@router.delete("/surveys/{survey_id}")
def delete_survey(survey_id: int)

# survey_service.py
def get_survey_statistics(db: Session, survey_id: int) -> dict
def export_survey_data(db: Session, survey_id: int) -> dict
def generate_qr_code(survey_id: int) -> bytes
```

**数据流**:
1. 创建问卷 → surveys表
2. 添加题目 → survey_questions表
3. 发布问卷 → 更新status
4. 收集答案 → survey_answers表
5. 数据分析 → 统计计算

---

### 3. 题库管理模块 (Question Bank Module)

**位置**: `backend/app/api/question_api.py`

**核心函数**:
```python
# question_api.py
@router.post("/questions/", response_model=schemas.QuestionResponse)
def create_global_question(question: schemas.QuestionCreate)

@router.get("/questions/", response_model=schemas.QuestionListResponse)
def read_global_questions(skip: int = 0, limit: int = 100, type: str = None)

@router.post("/organizations/{org_id}/questions/")
def create_organization_question(org_id: int, question: schemas.QuestionCreate)

@router.get("/organizations/{org_id}/questions/")
def read_organization_questions(org_id: int)

@router.put("/questions/{question_id}")
def update_question(question_id: int, question: schemas.QuestionUpdate)

@router.delete("/questions/{question_id}")
def delete_question(question_id: int)
```

**题目类型**:
- `single_choice`: 单选题
- `multi_choice`: 多选题
- `text_input`: 文本输入
- `number_input`: 数字输入
- `sort_order`: 排序题
- `conditional`: 关联题（条件触发）

**数据流**:
1. 创建题目 → questions表
2. 设置分类 → 关联categories
3. 添加标签 → question_tags表
4. 组织题库 → 设置organization_id
5. 引用题目 → survey_questions表

---

### 4. 数据分析模块 (Analytics Module)

**位置**: `backend/app/api/analytics_api.py`, `backend/app/services/statistics_service.py`

**核心函数**:
```python
# analytics_api.py
@router.get("/surveys/{survey_id}/analytics")
def get_survey_analytics(survey_id: int)

@router.get("/surveys/{survey_id}/statistics")
def get_question_statistics(survey_id: int, question_id: int = None)

@router.get("/surveys/{survey_id}/charts")
def get_chart_data(survey_id: int, chart_type: str = "bar")

# statistics_service.py
def calculate_basic_statistics(answers: List[models.SurveyAnswer]) -> dict
def calculate_score_distribution(answers: List[models.SurveyAnswer]) -> dict
def calculate_department_statistics(db: Session, survey_id: int) -> dict
def generate_comparison_data(db: Session, survey_ids: List[int]) -> dict
```

**分析类型**:
- 基础统计（均值、中位数、标准差）
- 选项分布（单选/多选题）
- 得分分布（评分题）
- 部门对比
- 组织对比
- 时间趋势

**图表类型**:
- 柱状图 (Bar Chart)
- 饼图 (Pie Chart)
- 折线图 (Line Chart)
- 雷达图 (Radar Chart)

---

### 5. LLM智能分析模块 (LLM Analysis Module)

**位置**: `backend/app/api/llm_api.py`, `backend/app/services/llm_service.py`

**核心函数**:
```python
# llm_api.py
@router.post("/surveys/{survey_id}/ai-summary")
def generate_ai_summary(survey_id: int)

@router.post("/surveys/{survey_id}/compare-analysis")
def generate_comparison_analysis(survey_id: int, compare_survey_ids: List[int])

# llm_service.py
def generate_survey_summary(db: Session, survey_id: int) -> str
def analyze_text_answers(answers: List[str]) -> dict
def generate_insights(statistics: dict) -> str
def compare_organizations(db: Session, org_ids: List[int]) -> str
```

**集成服务**: OpenRouter API

**分析功能**:
- 问卷数据总结
- 文本答案分析
- 趋势洞察
- 企业对比分析
- 改进建议

---

### 6. 组织管理模块 (Organization Module)

**位置**: `backend/app/api/org_api.py`

**核心函数**:
```python
# org_api.py
@router.post("/organizations/", response_model=schemas.OrganizationResponse)
def create_organization(org: schemas.OrganizationCreate)

@router.get("/organizations/", response_model=List[schemas.OrganizationResponse])
def read_organizations()

@router.post("/organizations/{org_id}/members")
def add_member(org_id: int, user_id: int, role: str = "member")

@router.get("/organizations/{org_id}/members")
def get_members(org_id: int)

@router.delete("/organizations/{org_id}/members/{user_id}")
def remove_member(org_id: int, user_id: int)
```

**权限级别**:
- `owner`: 组织所有者（完全权限）
- `admin`: 管理员（管理权限）
- `member`: 普通成员（查看权限）

---

### 7. 答案收集模块 (Answer Collection Module)

**位置**: `backend/app/api/answer_api.py`

**核心函数**:
```python
# answer_api.py
@router.post("/surveys/{survey_id}/answers")
def submit_answers(survey_id: int, answers: List[schemas.AnswerCreate])

@router.post("/surveys/{survey_id}/answers/save")
def save_progress(survey_id: int, answers: List[schemas.AnswerCreate])

@router.get("/surveys/{survey_id}/answers/{participant_id}")
def get_participant_answers(survey_id: int, participant_id: int)

@router.get("/surveys/{survey_id}/answers")
def get_all_answers(survey_id: int)
```

**数据流**:
1. 用户填写问卷
2. 保存进度（可选）
3. 提交答案 → survey_answers表
4. 计算得分（如果有评分）
5. 更新统计数据

---

### 8. 图表服务模块 (Chart Service Module)

**位置**: `backend/app/services/chart_service.py`

**核心函数**:
```python
def generate_bar_chart_data(statistics: dict) -> dict
def generate_pie_chart_data(distribution: dict) -> dict
def generate_line_chart_data(trend_data: List[dict]) -> dict
def generate_radar_chart_data(comparison: dict) -> dict
```

**前端对接**: ECharts

---

### 9. 分类标签模块 (Category & Tag Module)

**位置**: `backend/app/api/category_api.py`, `backend/app/api/tag_api.py`

**核心函数**:
```python
# category_api.py
@router.post("/categories/")
def create_category(category: schemas.CategoryCreate)

@router.get("/categories/tree")
def get_category_tree()

# tag_api.py
@router.post("/tags/")
def create_tag(tag: schemas.TagCreate)

@router.get("/tags/")
def get_tags()
```

---

## API接口

### 用户认证接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/login/access-token` | 用户登录 | ❌ |
| POST | `/register` | 用户注册 | ❌ |
| GET | `/users/me` | 获取当前用户信息 | ✅ |
| PUT | `/users/me` | 更新用户信息 | ✅ |

### 问卷管理接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/surveys/` | 创建问卷 | ✅ |
| GET | `/api/v1/surveys/` | 获取问卷列表 | ✅ |
| GET | `/api/v1/surveys/{survey_id}` | 获取问卷详情 | ❌ |
| PUT | `/api/v1/surveys/{survey_id}` | 更新问卷 | ✅ |
| DELETE | `/api/v1/surveys/{survey_id}` | 删除问卷 | ✅ |

### 题目管理接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/questions/` | 创建全局题目 | ✅ |
| GET | `/api/v1/questions/` | 获取题库列表 | ❌ |
| GET | `/api/v1/questions/{question_id}` | 获取题目详情 | ❌ |
| PUT | `/api/v1/questions/{question_id}` | 更新题目 | ✅ |
| DELETE | `/api/v1/questions/{question_id}` | 删除题目 | ✅ |
| POST | `/api/v1/surveys/{survey_id}/questions/` | 为问卷添加题目 | ✅ |
| GET | `/api/v1/surveys/{survey_id}/questions/` | 获取问卷题目列表 | ❌ |

### 答案提交接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/surveys/{survey_id}/answers` | 提交答案 | ❌ |
| POST | `/api/v1/surveys/{survey_id}/answers/save` | 保存进度 | ❌ |
| GET | `/api/v1/surveys/{survey_id}/answers` | 获取所有答案 | ✅ |

### 数据分析接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/surveys/{survey_id}/analytics` | 获取分析数据 | ✅ |
| GET | `/api/v1/surveys/{survey_id}/statistics` | 获取统计数据 | ✅ |
| GET | `/api/v1/surveys/{survey_id}/charts` | 获取图表数据 | ✅ |

### LLM智能分析接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/surveys/{survey_id}/ai-summary` | 生成AI总结 | ✅ |
| POST | `/api/v1/surveys/{survey_id}/compare-analysis` | 企业对比分析 | ✅ |

### 组织管理接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/organizations/` | 创建组织 | ✅ |
| GET | `/api/v1/organizations/` | 获取组织列表 | ✅ |
| GET | `/api/v1/organizations/{org_id}` | 获取组织详情 | ✅ |
| POST | `/api/v1/organizations/{org_id}/members` | 添加成员 | ✅ |
| GET | `/api/v1/organizations/{org_id}/members` | 获取成员列表 | ✅ |

---

## 启动方式

### 环境准备

#### 1. 克隆项目
```bash
git clone https://github.com/he2827987/SurveyProduct.git
cd SurveyProduct/survey_product_doc
```

#### 2. 安装Python依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

#### 4. 配置环境变量

**本地开发环境** (`.env.local`):
```bash
# 数据库配置
DATABASE_URL="mysql+pymysql://root@localhost:3306/survey_db"

# JWT配置
SECRET_KEY="your-super-secret-key-here"

# LLM配置
OPENROUTER_API_KEY="your-openrouter-api-key"

# 前端API地址
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**生产环境** (`.env.production`):
```bash
# 数据库配置
DATABASE_URL="mysql+pymysql://user:password@host:3306/survey_db"

# JWT配置
SECRET_KEY="production-secret-key"

# LLM配置
OPENROUTER_API_KEY="production-api-key"

# 前端API地址
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

#### 5. 初始化数据库
```bash
# 运行数据库迁移
python -m alembic upgrade head
```

---

### 本地开发启动

#### 方式1: 使用环境切换脚本（推荐）

```bash
# 切换到本地环境
./scripts/switch-env.sh local

# 启动后端（终端1）
cd survey_product_doc
source venv/bin/activate
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（终端2）
cd frontend
npm run dev
```

#### 方式2: 手动启动

**启动后端**:
```bash
cd survey_product_doc
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端**:
```bash
cd frontend
npm run dev
```

#### 方式3: 使用Makefile（如果可用）

```bash
# 启动所有服务
make dev

# 只启动后端
make backend

# 只启动前端
make frontend
```

---

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3000 | Vue.js应用 |
| 后端API | http://localhost:8000 | FastAPI服务 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 备用API文档 | http://localhost:8000/redoc | ReDoc |
| 健康检查 | http://localhost:8000/api/v1/health | Health Check |

---

### 生产环境部署

#### 使用Render部署（推荐）

**准备工作**:
1. 确保所有代码已推送到GitHub
2. 准备外部MySQL数据库（阿里云RDS/AWS RDS等）
3. 获取OpenRouter API密钥

**部署步骤**:

1. **切换到生产环境配置**
```bash
./scripts/switch-env.sh production
```

2. **提交代码**
```bash
git add .
git commit -m "feat: 准备生产环境部署"
git push origin main
```

3. **在Render Dashboard中配置**
   - 访问 https://dashboard.render.com
   - 点击 "New +" → "Web Service"
   - 连接GitHub仓库
   - 使用`render.yaml`配置（自动检测）

4. **配置环境变量**（在Render Dashboard中）
   - `DATABASE_URL`: MySQL连接字符串
   - `SECRET_KEY`: JWT密钥
   - `OPENROUTER_API_KEY`: LLM API密钥
   - `ENVIRONMENT`: production

5. **验证部署**
   - 检查部署日志
   - 访问 `https://your-app.onrender.com/api/v1/health`
   - 访问 `https://your-app.onrender.com/docs`

**自动部署流程**:
```
GitHub Push → Render自动检测 → 构建应用 → 运行迁移 → 启动服务
```

---

### 快速部署脚本

**一键部署到Render**:
```bash
./deploy_to_render.sh
```

脚本执行内容:
1. 检查Git状态
2. 切换到生产环境
3. 提交更改
4. 推送到GitHub
5. 触发Render自动部署

---

## 部署流程

### CI/CD流程

```mermaid
graph LR
    A[本地开发] --> B[切换到生产环境]
    B --> C[Git提交]
    C --> D[推送到GitHub]
    D --> E[Render检测更新]
    E --> F[构建前端]
    F --> G[安装Python依赖]
    G --> H[运行数据库迁移]
    H --> I[启动FastAPI]
    I --> J[健康检查]
    J --> K[部署完成]
```

### GitHub Actions工作流

**位置**: `.github/workflows/run-surveyproduct.yml`

**触发条件**:
- Push到main分支
- Pull Request到main分支

**执行步骤**:
1. 设置Python 3.11环境
2. 设置Node.js 18环境
3. 启动MySQL 8.0服务
4. 安装后端依赖
5. 安装前端依赖
6. 运行数据库迁移
7. 启动后端服务
8. 构建前端应用

### Render部署配置

**位置**: `render.yaml`

```yaml
services:
  - type: web
    name: survey-product-backend
    env: python
    plan: free
    buildCommand: |
      npm install --prefix frontend &&
      npm run build --prefix frontend &&
      pip install -r requirements.txt
    startCommand: cd survey_product_doc && python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: "mysql+pymysql://..."
      - key: SECRET_KEY
        generateValue: true
      - key: OPENROUTER_API_KEY
        value: "sk-or-v1-..."
      - key: ENVIRONMENT
        value: "production"
    healthCheckPath: /api/v1/health
```

---

## 环境管理

### 环境切换工作流

**切换到本地环境**:
```bash
./scripts/switch-env.sh local
```

**切换到生产环境**:
```bash
./scripts/switch-env.sh production
```

**效果**:
- 后端: 切换`.env`文件内容
- 前端: 使用对应的环境变量文件

### Git Hooks

**Pre-commit Hook**:
- 检查当前环境配置
- 如果是本地配置，提示是否切换到生产环境
- 防止意外提交错误配置

**安装Hooks**:
```bash
./scripts/setup-hooks.sh
```

---

## 数据库迁移

### Alembic迁移管理

**创建新迁移**:
```bash
alembic revision --autogenerate -m "描述信息"
```

**执行迁移**:
```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision>

# 降级一个版本
alembic downgrade -1
```

**查看迁移历史**:
```bash
alembic history --verbose
```

**查看当前版本**:
```bash
alembic current
```

### 重要迁移版本

| 版本ID | 说明 | 日期 |
|--------|------|------|
| dad85b68f6ef | 创建初始表 | 2025-07-09 |
| cefc2140f628 | 添加问卷题目关联表 | 2025-08-20 |
| 23bd084b04a7 | 添加题目分类表 | 2025-08-20 |
| d99b3a4c5b1f | 添加关联题字段 | 2025-12-15 |
| e4f96b9601ef | 合并时间和题目类型分支 | 2026-01-08 |
| 492677f1501f | 合并多个heads | 2026-01-10 |

---

## 常见问题

### 1. 数据库连接失败

**问题**: `Can't connect to MySQL server`

**解决方案**:
- 检查MySQL服务是否启动
- 验证`DATABASE_URL`配置是否正确
- 确认数据库用户权限

### 2. 前端无法调用API

**问题**: CORS错误或404错误

**解决方案**:
- 检查后端CORS配置
- 确认API地址配置正确
- 验证前端代理配置（开发环境）

### 3. Alembic迁移失败

**问题**: `Can't locate revision`

**解决方案**:
- 检查所有迁移文件是否完整
- 运行`alembic heads`查看当前heads
- 如有多个heads，创建merge migration

### 4. JWT认证失败

**问题**: `Invalid token`

**解决方案**:
- 检查`SECRET_KEY`配置
- 确认token未过期
- 验证token格式正确

---

## 开发规范

### 代码结构规范

1. **API路由**: 所有API路由放在`backend/app/api/`目录
2. **数据模型**: SQLAlchemy模型放在`backend/app/models/`目录
3. **数据验证**: Pydantic模型放在`backend/app/schemas/`目录
4. **业务逻辑**: 复杂业务逻辑放在`backend/app/services/`目录
5. **数据库操作**: CRUD操作放在`backend/app/crud.py`

### API命名规范

- 使用REST风格
- 路径使用小写字母和连字符
- 资源名使用复数形式
- 例如: `/api/v1/surveys/{survey_id}/questions/`

### 数据库命名规范

- 表名使用小写字母和下划线
- 主键统一使用`id`
- 时间戳字段使用`created_at`和`updated_at`
- 外键使用`表名_id`格式

---

## 性能优化

### 数据库优化

1. **索引优化**: 为常用查询字段添加索引
2. **查询优化**: 使用JOIN而非多次查询
3. **连接池**: 使用SQLAlchemy连接池
4. **缓存**: 对静态数据使用缓存

### API优化

1. **分页**: 所有列表接口支持分页
2. **字段选择**: 只返回必要字段
3. **批量操作**: 提供批量创建/更新接口
4. **异步处理**: 耗时操作使用后台任务

---

## 安全措施

### 认证授权

- **JWT Token**: 使用JWT进行身份认证
- **密码加密**: 使用bcrypt加密密码
- **权限控制**: 基于角色的访问控制（RBAC）

### 数据安全

- **输入验证**: 使用Pydantic验证所有输入
- **SQL注入防护**: 使用ORM避免SQL注入
- **XSS防护**: 前端对用户输入进行转义
- **HTTPS**: 生产环境强制使用HTTPS

---

## 监控日志

### 日志配置

**位置**: `backend/app/main.py`

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康检查

**端点**: `/api/v1/health`

**返回**:
```json
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-01-10T10:00:00Z"
}
```

---

## 联系方式

- **项目地址**: https://github.com/he2827987/SurveyProduct
- **文档**: 查看项目根目录的各个MD文件
- **问题反馈**: 通过GitHub Issues提交

---

## 更新日志

### v1.0.0 (2026-01-10)
- ✅ 完成基础功能开发
- ✅ 实现问卷创建和管理
- ✅ 实现数据分析功能
- ✅ 集成LLM智能分析
- ✅ 完成Render部署配置
- ✅ 完善文档和测试

---

**文档版本**: v1.0.0  
**最后更新**: 2026-01-10  
**维护者**: SurveyProduct Team
