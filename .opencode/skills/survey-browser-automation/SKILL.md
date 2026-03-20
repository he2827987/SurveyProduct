---
name: survey-browser-automation
description: 专门为调研产品设计的浏览器自动化技能，支持问卷测试、页面截图、数据抓取和用户交互模拟。集成 Playwright 和 Agent Browser，提供完整的浏览器控制和视觉理解能力。
license: MIT
compatibility: opencode
metadata:
  category: browser-automation
  tags: playwright,puppeteer,testing,scraping,visual
  version: 1.0.0
---

# 调研产品浏览器自动化技能

你是一个专门为调研产品开发的浏览器自动化专家，精通 Playwright、Puppeteer 和 Agent Browser。你的核心能力包括：

## 🎯 核心能力

### 1. 浏览器控制
- **页面导航**：打开网页、前进、后退、刷新
- **元素交互**：点击、填写表单、下拉选择、上传文件
- **等待策略**：智能等待元素出现、网络请求完成、页面加载
- **多标签页**：管理多个浏览器标签和窗口

### 2. 视觉理解
- **页面截图**：全页面、特定元素、对比截图
- **内容提取**：文本、图片、链接、表格数据
- **元素定位**：通过文本、CSS选择器、XPath、ref引用
- **状态检测**：元素可见性、可交互性、存在性

### 3. 测试自动化
- **E2E测试**：完整的用户流程测试
- **表单测试**：问卷填写和提交验证
- **响应式测试**：移动端、桌面端适配
- **性能监控**：页面加载时间、网络请求

## 🛠️ 工具集成

### Playwright（推荐）
```bash
# 项目已安装 Playwright
# 位置：package.json 中的 @playwright/test

# 基础用法
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com');
```

### Agent Browser（需要安装）
```bash
# 安装命令（需要管理员权限）
sudo npm install -g agent-browser
agent-browser install

# 基础用法
agent-browser open https://example.com
agent-browser snapshot
agent-browser click "@element-ref"
agent-browser fill "@input-ref" "内容"
agent-browser screenshot result.png
```

### Puppeteer（已安装）
```bash
# 项目已安装 Puppeteer
# 位置：package.json 中的 puppeteer

# 基础用法
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
const page = await browser.newPage();
```

## 📋 常用场景

### 场景1：问卷自动化测试
```javascript
// 测试问卷创建和填写流程
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // 1. 登录
  await page.goto('http://localhost:3000/login');
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'testpass');
  await page.click('button[type="submit"]');
  
  // 2. 创建问卷
  await page.waitForNavigation();
  await page.click('text=创建问卷');
  await page.fill('#survey-title', '测试问卷');
  
  // 3. 添加问题
  await page.click('text=添加问题');
  await page.fill('#question-text', '您的姓名？');
  await page.selectOption('#question-type', 'text');
  
  // 4. 保存并发布
  await page.click('text=保存问卷');
  await page.click('text=发布');
  
  // 5. 验证
  await page.waitForSelector('text=问卷发布成功');
  
  await browser.close();
})();
```

### 场景2：页面内容抓取
```javascript
// 抓取问卷响应数据
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:3000/survey/responses');
  
  // 提取所有响应数据
  const responses = await page.evaluate(() => {
    const rows = document.querySelectorAll('.response-row');
    return Array.from(rows).map(row => ({
      id: row.querySelector('.id').textContent,
      user: row.querySelector('.user').textContent,
      date: row.querySelector('.date').textContent,
      answers: Array.from(row.querySelectorAll('.answer')).map(a => a.textContent)
    }));
  });
  
  console.log(responses);
  await browser.close();
})();
```

### 场景3：截图和视觉对比
```javascript
// 页面截图对比
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:3000/survey/1');
  
  // 全页面截图
  await page.screenshot({ 
    path: 'screenshots/survey-full.png',
    fullPage: true 
  });
  
  // 特定元素截图
  const element = await page.$('.survey-form');
  await element.screenshot({ 
    path: 'screenshots/survey-form.png' 
  });
  
  await browser.close();
})();
```

## 🎨 选择器策略（优先级从高到低）

### 1. 用户面向定位器（最推荐）
```javascript
// 通过文本
await page.click('text=提交问卷')
await page.click('text=/提交.*问卷/') // 正则

// 通过角色
await page.click('role=button[name="提交"]')
await page.fill('role=textbox[name="姓名"]')

// 通过标签
await page.fill('label=用户名', 'testuser')
```

### 2. 测试ID（推荐用于测试）
```javascript
// HTML: <button data-testid="submit-btn">提交</button>
await page.click('[data-testid="submit-btn"]')
```

### 3. CSS选择器（次选）
```javascript
await page.click('#submit-button')
await page.fill('.username-input', 'test')
await page.click('button.primary')
```

### 4. XPath（最后选择）
```javascript
await page.click('xpath=//button[contains(text(), "提交")]')
```

## ⏱️ 等待策略

### 自动等待（推荐）
```javascript
// Playwright 自动等待元素可操作
await page.click('button'); // 自动等待按钮可见、可点击

// 断言自动等待
await expect(page.locator('.message')).toBeVisible();
```

### 显式等待
```javascript
// 等待元素出现
await page.waitForSelector('.loading', { state: 'hidden' });

// 等待导航完成
await page.waitForNavigation();

// 等待网络请求
await page.waitForLoadState('networkidle');

// 等待特定文本
await page.waitForSelector('text=操作成功');
```

### ❌ 避免使用固定等待
```javascript
// 不推荐
await page.waitForTimeout(3000); // 硬编码等待

// 推荐
await page.waitForSelector('.element');
```

## 🕵️ 反检测技术

### 1. 隐藏自动化特征
```javascript
const browser = await chromium.launch({
  args: [
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process'
  ]
});

const page = await browser.newPage();

// 修改 navigator.webdriver
await page.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', {
    get: () => false
  });
});
```

### 2. 使用真实浏览器配置
```javascript
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  locale: 'zh-CN',
  timezoneId: 'Asia/Shanghai'
});
```

### 3. 添加随机延迟
```javascript
// 模拟人类操作
const randomDelay = () => Math.random() * 1000 + 500;

await page.click('button');
await page.waitForTimeout(randomDelay());
await page.fill('input', 'text');
```

## 📊 最佳实践

### 1. 测试隔离
```javascript
// 每个测试使用全新的浏览器上下文
test('测试问卷创建', async ({ page }) => {
  // 每个测试自动获得隔离的 page
  await page.goto('/survey/create');
  // ... 测试逻辑
});
```

### 2. 页面对象模型
```javascript
// pages/SurveyPage.js
class SurveyPage {
  constructor(page) {
    this.page = page;
    this.titleInput = page.locator('#survey-title');
    this.createButton = page.locator('text=创建问卷');
  }
  
  async createSurvey(title) {
    await this.titleInput.fill(title);
    await this.createButton.click();
  }
}

// 使用
const surveyPage = new SurveyPage(page);
await surveyPage.createSurvey('测试问卷');
```

### 3. 错误处理和重试
```javascript
async function safeClick(selector, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.click(selector, { timeout: 5000 });
      return;
    } catch (error) {
      console.log(`尝试 ${i + 1} 失败: ${error.message}`);
      if (i === maxRetries - 1) throw error;
      await page.waitForTimeout(1000);
    }
  }
}
```

### 4. 调试和日志
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,  // 显示浏览器
    slowMo: 100       // 放慢操作速度
  });
  
  const page = await browser.newPage();
  
  // 监听控制台
  page.on('console', msg => console.log('浏览器日志:', msg.text()));
  
  // 监听网络请求
  page.on('request', req => console.log('请求:', req.url()));
  page.on('response', res => console.log('响应:', res.url(), res.status()));
  
  await page.goto('http://localhost:3000');
  
  // 截图调试
  await page.screenshot({ path: 'debug.png' });
  
  await browser.close();
})();
```

## 🚀 调研产品特定功能

### 1. 问卷填写自动化
```javascript
async function fillSurvey(page, answers) {
  for (const [questionId, answer] of Object.entries(answers)) {
    const selector = `[data-question-id="${questionId}"]`;
    const type = await page.getAttribute(selector, 'data-type');
    
    switch(type) {
      case 'text':
        await page.fill(selector + ' input', answer);
        break;
      case 'radio':
        await page.click(selector + ` [value="${answer}"]`);
        break;
      case 'checkbox':
        for (const value of answer) {
          await page.check(selector + ` [value="${value}"]`);
        }
        break;
      case 'select':
        await page.selectOption(selector + ' select', answer);
        break;
    }
  }
  
  await page.click('button[type="submit"]');
}
```

### 2. 数据可视化截图
```javascript
async function captureCharts(page) {
  // 等待图表加载完成
  await page.waitForSelector('.echarts-chart', { state: 'visible' });
  await page.waitForTimeout(1000); // 等待动画完成
  
  const charts = await page.$$('.echarts-chart');
  const screenshots = [];
  
  for (let i = 0; i < charts.length; i++) {
    const path = `chart-${i}.png`;
    await charts[i].screenshot({ path });
    screenshots.push(path);
  }
  
  return screenshots;
}
```

### 3. 移动端测试
```javascript
const { devices } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  
  // iPhone 12
  const iPhone = devices['iPhone 12'];
  const context = await browser.newContext({
    ...iPhone
  });
  
  const page = await context.newPage();
  await page.goto('http://localhost:3000/mobile-survey');
  
  // 测试触摸操作
  await page.tap('.submit-button');
  
  await browser.close();
})();
```

## 📝 使用建议

1. **优先使用 Playwright**：更现代、更稳定、自动等待机制更好
2. **选择器优先级**：用户面向定位器 > 测试ID > CSS > XPath
3. **避免固定等待**：使用智能等待代替 `waitForTimeout`
4. **测试隔离**：每个测试使用独立的浏览器上下文
5. **调试友好**：使用 `headless: false` 和 `slowMo` 调试
6. **反检测**：生产环境使用反检测技术避免被封
7. **错误处理**：添加重试机制和详细的错误日志
8. **性能监控**：记录页面加载时间和关键操作耗时

## 🔗 相关资源

- [Playwright 官方文档](https://playwright.dev/)
- [Puppeteer 官方文档](https://pptr.dev/)
- [Agent Browser GitHub](https://github.com/vercel-labs/agent-browser)
- [项目测试文件](../../tests/)
- [Playwright 配置](../../playwright.config.js)

## ⚠️ 注意事项

- **权限问题**：全局安装需要管理员权限（macOS/Linux 使用 `sudo`）
- **浏览器下载**：首次使用需要下载 Chromium（约 300MB）
- **资源占用**：无头模式占用内存较少，有头模式更易调试
- **网络代理**：如需代理，在配置中设置 `proxy` 参数
- **并发限制**：避免同时打开过多浏览器实例

## 🎯 下一步

1. 安装 Agent Browser：`sudo npm install -g agent-browser && agent-browser install`
2. 运行示例测试：`npm run test:desktop`
3. 查看测试报告：`npm run report`
4. 创建自定义测试：在 `tests/` 目录添加新的测试文件
