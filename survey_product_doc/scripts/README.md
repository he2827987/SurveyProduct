
# 调试脚本说明

本目录包含项目开发过程中使用的调试和测试脚本。

## 脚本分类

### 🔧 核心功能测试脚本

#### `test_enterprise_compare_fix.py`
- **用途**: 测试企业对比功能修复
- **功能**: 
  - 测试公开组织API端点
  - 验证企业对比数据流
  - 检查组织命名功能
  - 创建测试数据
- **使用**: `python test_enterprise_compare_fix.py`

#### `test_organization_data.py`
- **用途**: 测试组织数据功能
- **功能**:
  - 测试组织API功能
  - 验证组织数据结构
  - 测试组织创建功能
  - 检查调研与组织关系
- **使用**: `python test_organization_data.py`

### 🧹 数据清理脚本

#### `clean_debug_surveys.py`
- **用途**: 清理调试调研数据
- **功能**:
  - 删除测试调研
  - 清理相关回答数据
  - 重置数据库状态
- **使用**: `python clean_debug_surveys.py`

#### `add_questions_to_surveys.py`
- **用途**: 为调研添加测试题目
- **功能**:
  - 创建测试题目
  - 关联题目到调研
  - 设置题目顺序
- **使用**: `python add_questions_to_surveys.py`

### 📊 数据分析测试脚本

#### `test_all.py`
- **用途**: 通用测试脚本，整合所有常用测试功能
- **功能**:
  - 测试基本连接性
  - 测试组织API
  - 测试调研API
  - 测试数据分析API
  - 测试企业对比数据
  - 测试移动端调研功能
  - 创建测试数据
- **使用**: `python test_all.py`

#### `test_analytics_api.py`
- **用途**: 测试数据分析API
- **功能**:
  - 测试分析数据获取
  - 验证图表数据格式
  - 检查AI总结功能
- **使用**: `python test_analytics_api.py`

## 使用说明

1. **运行前准备**:
   - 确保后端服务已启动 (`uvicorn main:app --reload`)
   - 确保数据库连接正常
   - 检查API端点可访问性

2. **脚本执行**:
   ```bash
   # 运行全面测试
   python test_all.py
   
   # 测试企业对比功能
   python test_enterprise_compare_fix.py
   
   # 测试组织数据
   python test_organization_data.py
   
   # 清理调试数据
   python clean_debug_surveys.py
   ```

3. **注意事项**:
   - 部分脚本会修改数据库数据，请谨慎使用
   - 建议在测试环境中运行
   - 重要数据请先备份

## 脚本维护

- 定期清理过时的测试脚本
- 更新脚本以适应API变化
- 保持脚本的文档说明
- 删除已修复问题的相关脚本

## 常见问题

1. **API认证错误**: 检查token是否有效
2. **数据库连接失败**: 确认数据库服务状态
3. **数据格式错误**: 检查API响应格式是否变化
