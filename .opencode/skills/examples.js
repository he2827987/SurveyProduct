/**
 * 调研产品浏览器自动化示例
 * 演示如何使用 Playwright 进行问卷测试
 */

const { chromium } = require('playwright');

/**
 * 示例1：问卷创建和发布测试
 */
async function testSurveyCreation() {
  const browser = await chromium.launch({ 
    headless: false,  // 显示浏览器便于观察
    slowMo: 100       // 放慢操作速度
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('📝 开始测试问卷创建流程...');
    
    // 1. 访问登录页
    console.log('1. 访问登录页面');
    await page.goto('http://localhost:3000/login');
    await page.screenshot({ path: 'screenshots/01-login.png' });
    
    // 2. 登录
    console.log('2. 执行登录');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass');
    await page.click('button[type="submit"]');
    
    // 等待跳转
    await page.waitForNavigation();
    await page.screenshot({ path: 'screenshots/02-dashboard.png' });
    
    // 3. 创建问卷
    console.log('3. 创建新问卷');
    await page.click('text=创建问卷');
    await page.waitForSelector('#survey-form');
    
    await page.fill('#survey-title', '用户满意度调查');
    await page.fill('#survey-description', '请填写您对我们服务的满意度');
    await page.screenshot({ path: 'screenshots/03-create-survey.png' });
    
    // 4. 添加问题
    console.log('4. 添加问题');
    await page.click('text=添加问题');
    
    // 第一个问题：单选题
    await page.fill('[data-question-index="0"] .question-text', '您的性别？');
    await page.selectOption('[data-question-index="0"] .question-type', 'radio');
    await page.fill('[data-question-index="0"] .option-1', '男');
    await page.fill('[data-question-index="0"] .option-2', '女');
    
    // 第二个问题：文本题
    await page.click('text=添加问题');
    await page.fill('[data-question-index="1"] .question-text', '您的建议？');
    await page.selectOption('[data-question-index="1"] .question-type', 'text');
    
    await page.screenshot({ path: 'screenshots/04-add-questions.png' });
    
    // 5. 保存并发布
    console.log('5. 保存并发布问卷');
    await page.click('text=保存问卷');
    await page.waitForSelector('text=问卷已保存');
    
    await page.click('text=发布问卷');
    await page.waitForSelector('text=问卷发布成功');
    await page.screenshot({ path: 'screenshots/05-published.png' });
    
    console.log('✅ 问卷创建测试完成！');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    await page.screenshot({ path: 'screenshots/error.png' });
  } finally {
    await browser.close();
  }
}

/**
 * 示例2：问卷填写测试
 */
async function testSurveySubmission() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('📝 开始测试问卷填写...');
    
    // 访问问卷页面
    await page.goto('http://localhost:3000/survey/1');
    
    // 填写单选题
    await page.click('input[value="male"]');
    
    // 填写文本题
    await page.fill('textarea[name="suggestion"]', '服务很好，继续保持！');
    
    // 提交问卷
    await page.click('button[type="submit"]');
    
    // 验证提交成功
    await page.waitForSelector('text=提交成功');
    
    console.log('✅ 问卷填写测试完成！');
    
  } finally {
    await browser.close();
  }
}

/**
 * 示例3：数据提取
 */
async function extractSurveyData() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('📊 开始提取问卷数据...');
    
    await page.goto('http://localhost:3000/survey/1/responses');
    
    // 提取所有响应数据
    const responses = await page.evaluate(() => {
      const rows = document.querySelectorAll('.response-row');
      return Array.from(rows).map(row => ({
        id: row.querySelector('.response-id')?.textContent,
        user: row.querySelector('.response-user')?.textContent,
        date: row.querySelector('.response-date')?.textContent,
        answers: Array.from(row.querySelectorAll('.answer')).map(a => a.textContent)
      }));
    });
    
    console.log(`提取到 ${responses.length} 条响应数据`);
    console.log('示例数据:', responses[0]);
    
    return responses;
    
  } finally {
    await browser.close();
  }
}

/**
 * 示例4：移动端测试
 */
async function testMobileSurvey() {
  const { devices } = require('playwright');
  
  const browser = await chromium.launch();
  
  // 使用 iPhone 12 配置
  const iPhone = devices['iPhone 12'];
  const context = await browser.newContext({
    ...iPhone
  });
  
  const page = await context.newPage();
  
  try {
    console.log('📱 测试移动端问卷...');
    
    await page.goto('http://localhost:3000/survey/1');
    
    // 测试触摸操作
    await page.tap('input[value="female"]');
    await page.tap('textarea');
    await page.type('textarea', '移动端体验很好！');
    
    // 截图
    await page.screenshot({ path: 'screenshots/mobile-survey.png' });
    
    console.log('✅ 移动端测试完成！');
    
  } finally {
    await browser.close();
  }
}

/**
 * 示例5：批量截图对比
 */
async function captureScreenshots() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('📸 开始批量截图...');
    
    const pages = [
      { url: 'http://localhost:3000', name: 'homepage' },
      { url: 'http://localhost:3000/login', name: 'login' },
      { url: 'http://localhost:3000/dashboard', name: 'dashboard' },
      { url: 'http://localhost:3000/survey/create', name: 'create-survey' }
    ];
    
    for (const pageInfo of pages) {
      await page.goto(pageInfo.url);
      await page.waitForLoadState('networkidle');
      await page.screenshot({ 
        path: `screenshots/${pageInfo.name}.png`,
        fullPage: true 
      });
      console.log(`  ✅ ${pageInfo.name}.png`);
    }
    
    console.log('✅ 批量截图完成！');
    
  } finally {
    await browser.close();
  }
}

// 导出函数
module.exports = {
  testSurveyCreation,
  testSurveySubmission,
  extractSurveyData,
  testMobileSurvey,
  captureScreenshots
};

// 如果直接运行此文件
if (require.main === module) {
  console.log('选择要运行的示例：');
  console.log('1. 问卷创建测试');
  console.log('2. 问卷填写测试');
  console.log('3. 数据提取');
  console.log('4. 移动端测试');
  console.log('5. 批量截图');
  
  const example = process.argv[2] || '1';
  
  switch(example) {
    case '1':
      testSurveyCreation();
      break;
    case '2':
      testSurveySubmission();
      break;
    case '3':
      extractSurveyData();
      break;
    case '4':
      testMobileSurvey();
      break;
    case '5':
      captureScreenshots();
      break;
    default:
      console.log('请提供有效的示例编号 (1-5)');
  }
}
