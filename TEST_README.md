# 🤖 智能自动化测试系统

像真人一样操作浏览器并理解画面的自动化测试框架

## ✨ 特性

- 🎭 **真人模拟**: 智能等待、自然输入、页面分析
- 📸 **视觉理解**: 自动截图、DOM分析、页面状态识别
- 🖥️ **多端支持**: 桌面端 + 移动端测试
- 🔐 **智能认证**: 自动登录、状态保存
- 📊 **详细报告**: HTML报告 + JSON数据 + 截图

## 🚀 快速开始

### 1. 安装依赖
```bash
npm install
npx playwright install webkit
```

### 2. 启动服务
```bash
cd frontend && npm run dev &
cd ../backend && python -m uvicorn app.main:app --reload &
```

### 3. 运行测试
```bash
node run-tests.js
```

## 📁 项目结构

```
tests/
├── helpers/              # 辅助工具
│   ├── browser-helper.js   # 浏览器操作
│   ├── auth-helper.js      # 认证处理
│   └── visual-debug.js     # 视觉调试
└── e2e/                  # 测试场景
    ├── auth.spec.js        # 认证测试
    ├── survey.spec.js      # 问卷测试
    ├── analysis.spec.js    # 分析测试
    └── mobile.spec.js      # 移动端测试
```

## 🎯 测试命令

```bash
node run-tests.js              # 运行所有测试
npm run test:auth             # 认证测试
npm run test:survey           # 问卷测试
npm run test:analysis         # 分析测试
npm run test:mobile           # 移动端测试
npm run report                # 查看报告
```

## 📸 截图位置

所有测试截图自动保存到:
```
~/Downloads/Opencode/SurveyProduct/
```

## 🔧 配置

### 修改登录账号
编辑 `tests/helpers/auth-helper.js`:
```javascript
this.credentials = {
  email: 'your-email@example.com',
  password: 'your-password'
};
```

### 修改截图目录
编辑 `tests/helpers/browser-helper.js`:
```javascript
this.screenshotDir = '/your/custom/path';
```

### 浏览器配置
编辑 `playwright.config.js` 更改:
- 视口大小
- 浏览器类型
- 超时设置

## 📊 如何工作

### 我如何"看"到页面

1. **操作执行** → Playwright控制浏览器
2. **截图捕获** → 保存画面到文件
3. **DOM提取** → 获取页面元素信息
4. **信息返回** → 截图路径 + 元数据给我
5. **智能决策** → 我分析后决定下一步

### 示例流程

```
用户请求: "测试登录功能"
    ↓
我生成测试脚本
    ↓
脚本执行: 打开页面 → 截图
    ↓
脚本返回: 截图路径 + 页面信息
    ↓
我分析: 发现登录表单
    ↓
脚本执行: 填写邮箱密码 → 截图
    ↓
我分析: 表单填写正确
    ↓
脚本执行: 点击登录 → 截图
    ↓
我分析: 登录成功 → 继续测试
```

## 🐛 故障排除

### 浏览器安装失败
```bash
# 尝试使用镜像
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
  npx playwright install webkit
```

### 找不到元素
- 检查 `waitForTimeout` 设置
- 增加等待时间到3-5秒
- 查看截图确认页面加载

### Vue应用未加载
- 确认前端服务已启动
- 检查 http://localhost:3000 是否可访问
- 查看浏览器控制台错误

## 📚 详细文档

- [完整测试报告](./AUTOMATED_TEST_REPORT.md)
- [Playwright配置](./playwright.config.js)
- [测试日志](./test-output.log)

## 🎓 学习资源

- [Playwright文档](https://playwright.dev)
- [自动化测试最佳实践](https://playwright.dev/docs/best-practices)

---

**创建时间**: 2026-03-10
**版本**: 1.0.0
**维护者**: OpenCode AI
