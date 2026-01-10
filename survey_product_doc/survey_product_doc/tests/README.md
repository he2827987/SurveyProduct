# 测试脚本说明

本目录包含了调研平台的所有测试脚本，按照功能模块进行了分类整理。

## 目录结构

```
tests/
├── README.md                    # 本说明文件
├── demo_analytics.py            # 数据分析功能演示
├── demo_llm_summary.py          # LLM自动总结功能演示
├── api/                         # API测试脚本
│   ├── test_api_simple.py       # 简单API测试
│   ├── test_login.py            # 登录功能测试
│   ├── test_new_apis.py         # 新API功能测试
│   ├── test_simple_endpoint.py  # 简单端点测试
│   └── test_imports.py          # 导入功能测试
├── analytics/                   # 数据分析测试脚本
│   ├── test_analytics_api.py    # 数据分析API测试
│   └── test_advanced_analytics.py # 高级数据分析测试
├── llm/                         # LLM功能测试脚本
│   ├── test_llm_simple.py       # 简化LLM功能测试
│   └── test_llm_summary.py      # LLM总结功能测试
├── organization/                # 组织管理测试脚本
│   ├── test_org.py              # 组织功能测试
│   ├── test_org_simple.py       # 简单组织测试
│   ├── test_org_direct.py       # 直接组织测试
│   ├── test_org_no_auth.py      # 无认证组织测试
│   └── test_org_detailed.py     # 详细组织测试
├── department/                  # 部门管理测试脚本
│   ├── test_department_simple.py # 简单部门测试
│   ├── test_department_db.py    # 部门数据库测试
│   ├── test_department_no_auth.py # 无认证部门测试
│   ├── test_department_direct.py # 直接部门测试
│   ├── test_department_with_error_handling.py # 错误处理部门测试
│   └── test_department_create_simple.py # 简单部门创建测试
├── participant/                 # 参与者管理测试脚本
│   └── test_participant_api.py  # 参与者API测试
└── utils/                       # 工具和辅助测试脚本
    ├── test_db.py               # 数据库连接测试
    ├── test_permission.py       # 权限测试
    ├── create_test_data.py      # 测试数据创建
    ├── check_org_membership.py  # 组织成员关系检查
    └── check_question_ids.py    # 问题ID检查
```

## 测试脚本说明

### 演示脚本 (根目录)
- **demo_analytics.py**: 演示数据分析功能的完整流程
- **demo_llm_summary.py**: 演示LLM自动总结功能的完整流程

### API测试 (api/)
- **test_api_simple.py**: 测试基本的API连接和响应
- **test_login.py**: 测试用户登录功能
- **test_new_apis.py**: 测试新开发的API功能
- **test_simple_endpoint.py**: 测试简单的API端点
- **test_imports.py**: 测试模块导入功能

### 数据分析测试 (analytics/)
- **test_analytics_api.py**: 测试数据分析API的基本功能
- **test_advanced_analytics.py**: 测试高级数据分析功能，包括交叉分析、趋势分析等

### LLM功能测试 (llm/)
- **test_llm_simple.py**: 测试简化的LLM功能，包括问题生成和回答总结
- **test_llm_summary.py**: 测试完整的LLM总结功能，包括调研报告生成

### 组织管理测试 (organization/)
- **test_org.py**: 测试组织管理的基本功能
- **test_org_simple.py**: 测试简单的组织操作
- **test_org_direct.py**: 直接测试组织API
- **test_org_no_auth.py**: 测试无认证情况下的组织操作
- **test_org_detailed.py**: 详细测试组织管理的各种功能

### 部门管理测试 (department/)
- **test_department_simple.py**: 测试部门管理的基本功能
- **test_department_db.py**: 测试部门数据库操作
- **test_department_no_auth.py**: 测试无认证情况下的部门操作
- **test_department_direct.py**: 直接测试部门API
- **test_department_with_error_handling.py**: 测试部门操作的错误处理
- **test_department_create_simple.py**: 测试简单的部门创建功能

### 参与者管理测试 (participant/)
- **test_participant_api.py**: 测试参与者管理的API功能

### 工具和辅助测试 (utils/)
- **test_db.py**: 测试数据库连接和基本操作
- **test_permission.py**: 测试权限控制功能
- **create_test_data.py**: 创建测试数据
- **check_org_membership.py**: 检查组织成员关系
- **check_question_ids.py**: 检查问题ID，用于调试

## 运行测试

### 运行所有测试
```bash
# 运行演示脚本
python tests/demo_analytics.py
python tests/demo_llm_summary.py

# 运行API测试
python tests/api/test_login.py
python tests/api/test_new_apis.py

# 运行数据分析测试
python tests/analytics/test_analytics_api.py
python tests/analytics/test_advanced_analytics.py

# 运行LLM功能测试
python tests/llm/test_llm_simple.py
python tests/llm/test_llm_summary.py

# 运行组织管理测试
python tests/organization/test_org.py
python tests/organization/test_org_simple.py

# 运行部门管理测试
python tests/department/test_department_simple.py
python tests/department/test_department_api.py

# 运行参与者管理测试
python tests/participant/test_participant_api.py

# 运行工具测试
python tests/utils/test_db.py
python tests/utils/create_test_data.py
```

### 运行特定功能测试
```bash
# 测试数据分析功能
cd tests/analytics
python test_advanced_analytics.py

# 测试LLM功能
cd tests/llm
python test_llm_simple.py

# 测试组织管理
cd tests/organization
python test_org_simple.py
```

## 测试数据

测试脚本使用以下测试数据：
- **用户**: admin/admin123
- **组织ID**: 6
- **调研ID**: 1
- **问题ID**: 35, 36

## 注意事项

1. **环境要求**: 确保后端服务正在运行 (uvicorn backend.app.main:app --reload)
2. **数据库**: 确保数据库连接正常，测试数据已创建
3. **API密钥**: 确保OpenRouter API密钥已配置（用于LLM功能测试）
4. **权限**: 确保测试用户具有足够的权限

## 故障排除

### 常见问题
1. **连接错误**: 检查后端服务是否正在运行
2. **认证失败**: 检查用户名和密码是否正确
3. **权限错误**: 检查用户是否有访问相应组织的权限
4. **LLM错误**: 检查OpenRouter API密钥是否正确配置

### 调试技巧
1. 使用 `check_question_ids.py` 检查问题ID
2. 使用 `check_org_membership.py` 检查组织成员关系
3. 使用 `test_db.py` 检查数据库连接
4. 查看后端日志获取详细错误信息
