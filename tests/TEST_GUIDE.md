# SurveyProduct 测试执行指南

## 测试概览

本项目采用多层级测试策略，包括单元测试、集成测试、E2E测试、性能测试和安全测试。

## 目录结构

```
tests/
├── unit/                          # 单元测试
│   ├── backend/                   # 后端单元测试
│   │   ├── models/               # 模型测试
│   │   ├── services/             # 服务测试
│   │   └── crud/                 # CRUD测试
│   └── frontend/                 # 前端单元测试
│       ├── components/           # 组件测试
│       └── utils/                # 工具函数测试
├── integration/                   # 集成测试
│   ├── api/                      # API集成测试
│   ├── database/                 # 数据库集成测试
│   └── services/                 # 服务集成测试
├── e2e/                          # E2E测试 (Playwright)
│   ├── auth.spec.js              # 认证流程
│   ├── survey.spec.js            # 问卷流程
│   ├── analysis.spec.js          # 分析流程
│   └── mobile.spec.js            # 移动端测试
├── performance/                  # 性能测试
│   └── locustfile.py             # Locust脚本
├── security/                     # 安全测试
│   ├── test_sql_injection.py     # SQL注入测试
│   └── test_xss.py              # XSS攻击测试
├── fixtures/                     # 测试fixtures
├── conftest.py                   # pytest配置
└── pytest.ini                    # pytest配置
```

## 快速开始

### 安装测试依赖

```bash
# 后端测试依赖
pip install -r requirements.txt

# 前端测试依赖
cd frontend
npm install --save-dev vitest @vue/test-utils jsdom @vitest/coverage-c8
npm install
```

### 运行测试

#### 1. 运行所有测试

```bash
# 后端测试
pytest tests/ -v

# 前端测试
cd frontend
npm run test
```

#### 2. 运行特定类型的测试

```bash
# 单元测试
pytest tests/unit/ -v -m unit

# 集成测试
pytest tests/integration/ -v -m integration

# API测试
pytest tests/integration/api/ -v -m api

# 数据库测试
pytest tests/integration/database/ -v -m db

# 安全测试
pytest tests/security/ -v -m security

# 性能测试
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

#### 3. 运行E2E测试

```bash
# 运行所有E2E测试
npm run test

# 运行特定E2E测试
npm run test:auth
npm run test:survey
npm run test:analysis
npm run test:mobile
```

#### 4. 生成覆盖率报告

```bash
# 后端覆盖率
pytest tests/ --cov=backend --cov-report=html
open htmlcov/index.html

# 前端覆盖率
cd frontend
npm run test:coverage
```

#### 5. 查看E2E测试报告

```bash
npm run report
```

## 测试命令参考

### Pytest命令

```bash
# 基础命令
pytest                                    # 运行所有测试
pytest -v                                # 详细输出
pytest -s                                # 显示print输出
pytest -x                                # 遇到失败就停止
pytest --maxfail=3                      # 最多3个失败后停止

# 标记测试
pytest -m unit                           # 只运行标记为unit的测试
pytest -m "not slow"                     # 排除slow测试
pytest -m "api and not security"         # 组合标记

# 覆盖率
pytest --cov=backend                     # 生成覆盖率
pytest --cov=backend --cov-report=html   # HTML报告
pytest --cov=backend --cov-fail-under=80 # 低于80%则失败

# 并行运行
pytest -n auto                            # 自动并行
pytest -n 4                              # 4个worker

# 调试
pytest -pdb                              # 失败时进入调试器
pytest --trace                           # 进入Python调试器
pytest --lf                              # 只运行上次失败的测试
pytest --ff                              # 优先运行失败的测试
```

### Playwright命令

```bash
# 运行测试
npx playwright test                     # 运行所有测试
npx playwright test --headed            # 有头模式
npx playwright test --debug             # 调试模式
npx playwright test --project=chromium  # 指定浏览器

# UI模式
npx playwright test --ui               # 交互式UI

# 报告
npx playwright show-report              # 查看HTML报告

# 调试
npx playwright test --debug             # 调试器
npx playwright codegen                  # 生成测试代码

# 安装浏览器
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

### Locust命令

```bash
# 运行性能测试
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 无头模式
locust -f tests/performance/locustfile.py --headless --host=http://localhost:8000 -u 100 -r 10 -t 60s

# 参数说明：
# -u 100: 100个并发用户
# -r 10: 每秒增加10个用户
# -t 60s: 运行60秒
```

## CI/CD集成

### GitHub Actions配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npx playwright test
```

## 测试最佳实践

### 编写测试用例

1. **AAA模式**: Arrange-Act-Assert
```python
def test_create_survey():
    # Arrange: 准备测试数据
    survey_data = {"title": "测试"}
    
    # Act: 执行操作
    survey = create_survey(survey_data)
    
    # Assert: 验证结果
    assert survey.title == "测试"
```

2. **使用Fixtures**: 在`conftest.py`中定义可重用的fixtures

3. **命名规范**:
   - 测试文件: `test_*.py`
   - 测试类: `Test*`
   - 测试函数: `test_*`

4. **独立性**: 每个测试应该独立运行

5. **可重复性**: 测试结果应该可重复

### 测试数据管理

1. **使用测试数据库**: 使用内存SQLite数据库
2. **数据清理**: 使用`autouse` fixture自动清理
3. **Mock外部服务**: Mock LLM API等外部服务

### 性能优化

1. **并行执行**: 使用pytest-xdist并行运行测试
2. **选择性运行**: 使用标记只运行相关测试
3. **测试分组**: 将测试按模块分组

## 常见问题

### 1. 测试失败

```bash
# 查看详细错误
pytest -vvs

# 只运行失败的测试
pytest --lf

# 调试失败的测试
pytest --pdb
```

### 2. 数据库连接问题

```bash
# 检查数据库配置
pytest tests/integration/database/ -v

# 使用内存数据库
# 在conftest.py中已配置
```

### 3. E2E测试超时

```bash
# 增加超时时间
# 在playwright.config.js中修改
use: {
  actionTimeout: 10000,  # 10秒
  navigationTimeout: 30000  # 30秒
}
```

### 4. 测试环境变量

```bash
# 创建.env.test文件
cp .env.example .env.test

# 在测试中使用
pytest --env-file=.env.test
```

## 持续改进

### 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|----------|
| 后端模型 | 90%+ | 进行中 |
| 后端服务 | 80%+ | 进行中 |
| 后端API | 85%+ | 进行中 |
| 前端组件 | 70%+ | 待建立 |
| 前端工具 | 80%+ | 待建立 |

### 下一步行动

1. [ ] 完成所有单元测试
2. [ ] 建立前端测试框架
3. [ ] 完善E2E测试用例
4. [ ] 添加性能基准测试
5. [ ] 建立测试报告系统

## 联系方式

如有问题，请提交Issue或联系测试团队。
