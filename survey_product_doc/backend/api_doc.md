# 企业问卷调查系统后端API接口文档

## 用户与公司相关

### 用户注册
- 方法：POST
- 路径：/auth/register
- 请求参数：
```
{
  "username": "string",
  "password": "string",
  "company_name": "string"
}
```
- 返回：
```
{
  "id": 1,
  "username": "admin",
  "company_id": 1
}
```

### 用户登录
- 方法：POST
- 路径：/auth/login
- 请求参数：
```
{
  "username": "string",
  "password": "string"
}
```
- 返回：
```
{
  "id": 1,
  "username": "admin",
  "company_id": 1
}
```

---

## 调研与题库相关

### 创建调研
- 方法：POST
- 路径：/survey
- 请求参数：
```
{
  "title": "2024年员工满意度调查",
  "company_id": 1,
  "creator_id": 1
}
```
- 返回：
```
{
  "id": 1,
  "title": "2024年员工满意度调查"
}
```

### 创建题库题目
- 方法：POST
- 路径：/question
- 请求参数：
```
{
  "title": "你对公司环境满意吗？",
  "type": "single",
  "options": "[\"满意\",\"一般\",\"不满意\"]",
  "max_length": null,
  "tags": "满意度,环境",
  "company_id": 1
}
```
- 返回：
```
{
  "id": 1,
  "title": "你对公司环境满意吗？"
}
```

### 关联调研题目
- 方法：POST
- 路径：/survey-question
- 请求参数：
```
{
  "survey_id": 1,
  "question_id": 1,
  "order": 1
}
```
- 返回：
```
{
  "id": 1
}
```

---

## 答题与填写人相关

### 新建填写人
- 方法：POST
- 路径：/respondent
- 请求参数：
```
{
  "name": "张三",
  "department_id": 2,
  "position": "工程师",
  "survey_id": 1
}
```
- 返回：
```
{
  "id": 1
}
```

### 提交答题
- 方法：POST
- 路径：/answer
- 请求参数：
```
{
  "respondent_id": 1,
  "question_id": 1,
  "answer_text": "满意"
}
```
- 返回：
```
{
  "id": 1
}
```

---

## 大模型分析

### 生成分析总结
- 方法：POST
- 路径：/llm/summary
- 请求参数：
```
{
  "prompt": "请对本次调研结果进行总结分析",
  "model": "gpt-3.5-turbo"  // 可选
}
```
- 返回：
```
{
  // openrouter 返回的内容
}
``` 