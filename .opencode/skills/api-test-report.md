# API 接口测试报告

**生成时间**: 2026/3/20 16:48:30

## 📊 测试概览

- **总测试数**: 17
- **✅ 通过**: 12
- **❌ 失败**: 5
- **⚠️ 跳过**: 0
- **📈 通过率**: 70.59%
- **⏱️ 耗时**: 8.62 秒

## 📋 详细测试结果

| 序号 | 端点 | 方法 | 状态 | 消息 | 时间 |
|------|------|------|------|------|------|
| 1 | `/test` | GET | ❌ FAIL | 服务器健康检查失败: 未知错误 | 16:48:21 |
| 2 | `/api/v1/users/register` | POST | ✅ PASS | 用户注册成功: testuser_1773996501679 | 16:48:22 |
| 3 | `/api/v1/users/login/access-token` | POST | ✅ PASS | 用户登录成功，已获取认证 token | 16:48:22 |
| 4 | `/api/v1/users/me` | GET | ✅ PASS | 获取用户信息成功: testuser_1773996501679 | 16:48:22 |
| 5 | `/api/v1/organizations/` | GET | ✅ PASS | 获取组织列表成功，共 1 个组织 | 16:48:22 |
| 6 | `/api/v1/organizations/21` | GET | ✅ PASS | 获取组织详情成功: testuser_1773996501679的组织 | 16:48:22 |
| 7 | `/api/v1/surveys/` | GET | ✅ PASS | 获取问卷列表成功，共 0 个问卷 | 16:48:22 |
| 8 | `/api/v1/surveys/` | POST | ✅ PASS | 创建问卷成功 | 16:48:22 |
| 9 | `/api/v1/questions/` | GET | ✅ PASS | 获取问题列表成功，共 0 个问题 | 16:48:22 |
| 10 | `/api/v1/answers/` | GET | ❌ FAIL | 获取答案列表失败 | 16:48:22 |
| 11 | `/api/v1/organizations/21/departments` | GET | ✅ PASS | 获取部门列表成功，共 1 个部门 | 16:48:22 |
| 12 | `/api/v1/organizations/21/participants` | GET | ✅ PASS | 获取参与者列表成功，共 0 个参与者 | 16:48:22 |
| 13 | `/api/v1/analytics/` | GET | ✅ PASS | 分析 API 可用 | 16:48:22 |
| 14 | `/api/v1/tags/` | GET | ❌ FAIL | 获取标签列表失败 | 16:48:22 |
| 15 | `/api/v1/categories/` | GET | ❌ FAIL | 获取分类列表失败 | 16:48:22 |
| 16 | `/api/v1/llm/status` | GET | ❌ FAIL | LLM API 状态检查失败 | 16:48:22 |
| 17 | `/docs` | GET | ✅ PASS | API 文档页面加载成功，共发现 134 个 API 端点 | 16:48:30 |

## ❌ 失败的测试详情

### 1. GET /test

- **消息**: 服务器健康检查失败: 未知错误
- **时间**: 2026/3/20 16:48:21
- **详情**: 
```json
{
  "status": 200,
  "ok": true,
  "data": "<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <link rel=\"icon\" type=\"image/svg+xml\" href=\"/vite.svg\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Survey Product - 调研管理系统</title>\n    <script type=\"module\" crossorigin src=\"/assets/index-Bnm8pNvu.js\"></script>\n    <link rel=\"stylesheet\" crossorigin href=\"/assets/index-w7YXX6Kt.css\">\n  </head>\n  <body>\n    <div id=\"app\"></div>\n  </body>\n</html>\n"
}
```

### 2. GET /api/v1/answers/

- **消息**: 获取答案列表失败
- **时间**: 2026/3/20 16:48:22
- **详情**: 
```json
{
  "status": 404,
  "ok": false,
  "data": {
    "detail": "Not Found"
  }
}
```

### 3. GET /api/v1/tags/

- **消息**: 获取标签列表失败
- **时间**: 2026/3/20 16:48:22
- **详情**: 
```json
{
  "status": 404,
  "ok": false,
  "data": {
    "detail": "Not Found"
  }
}
```

### 4. GET /api/v1/categories/

- **消息**: 获取分类列表失败
- **时间**: 2026/3/20 16:48:22
- **详情**: 
```json
{
  "status": 404,
  "ok": false,
  "data": {
    "detail": "Not Found"
  }
}
```

### 5. GET /api/v1/llm/status

- **消息**: LLM API 状态检查失败
- **时间**: 2026/3/20 16:48:22
- **详情**: 
```json
{
  "status": 404,
  "ok": false,
  "data": {
    "detail": "Not Found"
  }
}
```


## 📸 截图

- [API 文档页面](.opencode/skills/api-docs-page.png)

## 📝 备注

- 测试用户: testuser_1773996501679
- 基础 URL: http://localhost:8000
- 文档 URL: http://localhost:8000/docs
