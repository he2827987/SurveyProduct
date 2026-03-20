# 🚀 浏览器自动化技能快速开始指南

## ✅ 已完成的安装

### 1. ✅ 现成技能（来自 LobeHub Marketplace）
- **位置**：`.opencode/skills/haniakrim21-everything-claude-code-browser-automation/`
- **功能**：Playwright 和 Puppeteer 浏览器自动化最佳实践
- **状态**：已安装并可用

### 2. ✅ 自定义技能（为调研产品设计）
- **位置**：`.opencode/skills/survey-browser-automation/`
- **功能**：专门针对调研产品的浏览器自动化、测试、截图、数据抓取
- **状态**：已创建并可用

### 3. ✅ 项目工具（已安装）
- ✅ **Playwright**：`@playwright/test@^1.58.2`
- ✅ **Puppeteer**：`puppeteer@^24.38.0`

## 🔧 可选：安装 Agent Browser

Agent Browser 是一个基于 Playwright 的 CLI 工具，提供更简单的命令行接口。

### 方式一：全局安装（需要管理员权限）
```bash
sudo npm install -g agent-browser
agent-browser install
```

### 方式二：本地安装（推荐）
```bash
npm install --save-dev agent-browser
npx agent-browser install
```

### 验证安装
```bash
# 如果全局安装
agent-browser --version

# 如果本地安装
npx agent-browser --version
```

## 📖 如何使用技能

### 方法1：直接调用（推荐）
在对话中直接告诉我你的需求，我会自动加载和使用这些技能：

**示例提示词：**
```
请帮我测试问卷创建流程：
1. 打开 http://localhost:3000/login
2. 登录用户名：testuser，密码：testpass
3. 点击"创建问卷"
4. 填写问卷标题："用户满意度调查"
5. 添加3个问题
6. 保存并发布
7. 验证发布成功
8. 截图保存结果
```

### 方法2：显式加载技能
```
使用 browser-automation 技能，帮我自动化测试登录功能
```

### 方法3：使用斜杠命令（如果支持）
```
/browser-automation 测试问卷提交功能
```

## 🎯 常用场景示例

### 场景1：E2E 测试
```bash
# 运行项目已有的测试
npm run test:desktop

# 运行特定测试
npm run test:auth  # 认证测试
npm run test:survey  # 问卷测试
```

### 场景2：快速原型测试
创建 `test-quick.js`：
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:3000');
  await page.screenshot({ path: 'homepage.png' });
  
  console.log('✅ 测试完成');
  await browser.close();
})();
```

运行：
```bash
node test-quick.js
```

### 场景3：使用 Agent Browser（如果已安装）
```bash
# 交互式浏览器控制
agent-browser open http://localhost:3000
agent-browser snapshot  # 查看页面元素
agent-browser click "@submit-btn"
agent-browser screenshot result.png
agent-browser close
```

## 📚 技能详细文档

### 现成技能文档
```bash
# 查看现成技能的完整说明
cat .opencode/skills/haniakrim21-everything-claude-code-browser-automation/SKILL.md
```

### 自定义技能文档
```bash
# 查看自定义技能的详细指南
cat .opencode/skills/survey-browser-automation/SKILL.md
```

## 🎨 选择器快速参考

| 优先级 | 类型 | 示例 | 说明 |
|--------|------|------|------|
| ⭐⭐⭐⭐⭐ | 用户面向 | `text=提交` | 最稳定，模拟用户视角 |
| ⭐⭐⭐⭐ | 测试ID | `[data-testid="submit"]` | 测试专用，不易变化 |
| ⭐⭐⭐ | 角色 | `role=button[name="提交"]` | 无障碍友好 |
| ⭐⭐ | CSS | `.submit-button` | 常用，但依赖样式 |
| ⭐ | XPath | `//button[@type="submit"]` | 最后选择 |

## ⏱️ 等待策略快速参考

| 策略 | 使用场景 | 示例 |
|------|----------|------|
| 自动等待 | 大多数情况 | `page.click('button')` |
| waitForSelector | 等待元素出现 | `page.waitForSelector('.loaded')` |
| waitForNavigation | 等待页面跳转 | `page.waitForNavigation()` |
| waitForLoadState | 等待网络空闲 | `page.waitForLoadState('networkidle')` |
| ❌ waitForTimeout | 尽量避免 | `page.waitForTimeout(3000)` |

## 🐛 调试技巧

### 1. 显示浏览器
```javascript
const browser = await chromium.launch({ 
  headless: false,  // 显示浏览器窗口
  slowMo: 100       // 放慢操作
});
```

### 2. 截图调试
```javascript
await page.screenshot({ path: 'debug.png', fullPage: true });
```

### 3. 控制台日志
```javascript
page.on('console', msg => console.log('浏览器:', msg.text()));
```

### 4. Playwright Inspector
```bash
# 使用调试模式运行
npx playwright test --debug
```

## 🔍 验证技能是否可用

运行以下命令查看已安装的技能：
```bash
# 列出项目技能
ls -la .opencode/skills/

# 应该看到：
# haniakrim21-everything-claude-code-browser-automation/
# survey-browser-automation/
```

## 📞 获取帮助

如果在使用过程中遇到问题，可以：

1. **查看技能文档**：阅读 SKILL.md 文件
2. **查看测试示例**：`tests/` 目录中的测试文件
3. **查看 Playwright 文档**：https://playwright.dev/
4. **直接询问**：在对话中描述你的需求，我会加载相应技能来帮助你

## 🎉 下一步建议

1. ✅ 技能已安装并可用
2. 📖 阅读 `survey-browser-automation/SKILL.md` 了解详细用法
3. 🧪 尝试一个简单的测试场景（如登录测试）
4. 📸 使用截图功能验证页面状态
5. 🔄 根据需要扩展自动化测试覆盖范围

---

**提示**：现在你可以直接在对话中提出浏览器自动化需求，我会自动使用这些技能来帮助你完成任务！
