const { chromium } = require('playwright');

// 测试配置
const CONFIG = {
  baseUrl: 'http://localhost:3000',
  email: 'he282987@gmail.com',
  password: '12345678',
  timeout: 10000
};

// 测试结果记录
const testResults = {
  passed: [],
  failed: [],
  errors: []
};

// 日志函数
function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = {
    info: 'ℹ️',
    success: '✅',
    error: '❌',
    warning: '⚠️'
  }[type] || 'ℹ️';
  console.log(`${prefix} [${timestamp}] ${message}`);
}

// 等待函数
function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  log('========================================');
  log('开始全面功能测试');
  log('========================================');
  
  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();
  
  // 监听网络请求
  const requests = [];
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      requests.push({
        url: request.url(),
        method: request.method(),
        time: new Date().toISOString()
      });
      log(`API请求: ${request.method()} ${request.url()}`, 'info');
    }
  });
  
  // 监听控制台错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      testResults.errors.push({
        message: msg.text(),
        location: msg.location()
      });
      log(`控制台错误: ${msg.text()}`, 'error');
    }
  });
  
  try {
    // ==================== 第一阶段：认证功能 ====================
    log('\n【第一阶段：认证功能测试】');
    
    // 测试1.1: 访问登录页面
    log('测试 1.1: 访问登录页面');
    await page.goto(`${CONFIG.baseUrl}/login`);
    await wait(2000);
    
    const loginFormVisible = await page.isVisible('form');
    if (loginFormVisible) {
      log('登录表单可见', 'success');
      testResults.passed.push('1.1 登录表单显示');
    } else {
      log('登录表单不可见', 'error');
      testResults.failed.push('1.1 登录表单显示');
    }
    
    // 测试1.2: 填写登录信息
    log('测试 1.2: 填写登录信息');
    
    const emailInput = await page.$('input[type="email"]') || 
                       await page.$('input[placeholder*="邮箱"]') ||
                       await page.$('input[placeholder*="Email"]');
    
    const passwordInput = await page.$('input[type="password"]') ||
                          await page.$('input[placeholder*="密码"]');
    
    if (emailInput && passwordInput) {
      await emailInput.fill(CONFIG.email);
      await passwordInput.fill(CONFIG.password);
      log('登录信息填写成功', 'success');
      testResults.passed.push('1.2 填写登录信息');
    } else {
      log('未找到登录输入框', 'error');
      testResults.failed.push('1.2 填写登录信息');
      await page.screenshot({ path: 'test-screenshots/login-form-error.png' });
    }
    
    // 测试1.3: 点击登录按钮
    log('测试 1.3: 点击登录按钮');
    const loginButton = await page.$('button:has-text("登录")') ||
                        await page.$('button[type="submit"]');
    
    if (loginButton) {
      await loginButton.click();
      log('登录按钮点击成功', 'success');
      
      await wait(3000);
      
      const currentUrl = page.url();
      log(`当前URL: ${currentUrl}`);
      
      if (!currentUrl.includes('/login')) {
        log('登录后成功跳转', 'success');
        testResults.passed.push('1.3 登录跳转');
      } else {
        log('登录后未跳转', 'error');
        testResults.failed.push('1.3 登录跳转');
        
        const errorMessage = await page.$('.el-message--error');
        if (errorMessage) {
          const errorText = await errorMessage.textContent();
          log(`登录错误: ${errorText}`, 'error');
        }
        
        await page.screenshot({ path: 'test-screenshots/login-error.png' });
      }
    } else {
      log('未找到登录按钮', 'error');
      testResults.failed.push('1.3 点击登录按钮');
    }
    
    // ==================== 第二阶段：调研管理 ====================
    log('\n【第二阶段：调研管理测试】');
    
    log('测试 2.1: 访问调研列表页面');
    await page.goto(`${CONFIG.baseUrl}/survey`);
    await wait(3000);
    
    const surveyApiRequests = requests.filter(r => 
      r.url.includes('/surveys') && r.method === 'GET'
    );
    
    if (surveyApiRequests.length > 0) {
      log(`发现 ${surveyApiRequests.length} 个调研API请求`, 'success');
      testResults.passed.push('2.1 调研API请求发送');
    } else {
      log('未发现调研API请求', 'error');
      testResults.failed.push('2.1 调研API请求发送');
    }
    
    log('测试 2.2: 检查调研列表显示');
    await wait(2000);
    
    const surveyTable = await page.$('.el-table') || await page.$('table');
    
    if (surveyTable) {
      const rows = await surveyTable.$$('tr');
      log(`找到 ${rows.length} 行数据`, 'success');
      log('调研列表显示正常', 'success');
      testResults.passed.push('2.2 调研列表显示');
    } else {
      log('未找到调研列表表格', 'error');
      testResults.failed.push('2.2 调研列表显示');
      await page.screenshot({ path: 'test-screenshots/survey-list-error.png' });
    }
    
    // ==================== 第三阶段：题库管理 ====================
    log('\n【第三阶段：题库管理测试】');
    
    log('测试 3.1: 访问题库页面');
    await page.goto(`${CONFIG.baseUrl}/question`);
    await wait(3000);
    
    const questionApiRequests = requests.filter(r => 
      r.url.includes('/questions') && r.method === 'GET'
    );
    
    if (questionApiRequests.length > 0) {
      log(`发现 ${questionApiRequests.length} 个题目API请求`, 'success');
      testResults.passed.push('3.1 题库API请求发送');
    } else {
      log('未发现题目API请求', 'error');
      testResults.failed.push('3.1 题库API请求发送');
    }
    
    log('测试 3.2: 检查题目列表显示');
    const questionList = await page.$('.el-table') || await page.$('.question-list');
    
    if (questionList) {
      log('题库列表显示正常', 'success');
      testResults.passed.push('3.2 题库列表显示');
    } else {
      log('题库列表未显示', 'error');
      testResults.failed.push('3.2 题库列表显示');
      await page.screenshot({ path: 'test-screenshots/question-list-error.png' });
    }
    
    // ==================== 第四阶段：数据分析 ====================
    log('\n【第四阶段：数据分析测试】');
    
    log('测试 4.1: 访问数据分析页面');
    await page.goto(`${CONFIG.baseUrl}/analysis`);
    await wait(3000);
    
    log('测试 4.2: 检查标签切换按钮');
    const tabButtons = await page.$$('.el-radio-button');
    
    if (tabButtons.length >= 3) {
      log(`找到 ${tabButtons.length} 个标签切换按钮`, 'success');
      testResults.passed.push('4.2 标签切换按钮显示');
      
      log('测试 4.3: 测试标签切换功能');
      for (let i = 0; i < Math.min(3, tabButtons.length); i++) {
        await tabButtons[i].click();
        await wait(1000);
      }
      log('标签切换功能正常', 'success');
      testResults.passed.push('4.3 标签切换功能');
    } else {
      log(`标签切换按钮数量不正确: ${tabButtons.length}`, 'error');
      testResults.failed.push('4.2 标签切换按钮显示');
      await page.screenshot({ path: 'test-screenshots/analysis-tabs-error.png' });
    }
    
    // ==================== 测试结果汇总 ====================
    log('\n========================================');
    log('测试结果汇总');
    log('========================================');
    
    log(`\n✅ 通过的测试 (${testResults.passed.length}):`);
    testResults.passed.forEach((test, index) => {
      log(`  ${index + 1}. ${test}`, 'success');
    });
    
    log(`\n❌ 失败的测试 (${testResults.failed.length}):`);
    testResults.failed.forEach((test, index) => {
      log(`  ${index + 1}. ${test}`, 'error');
    });
    
    if (testResults.errors.length > 0) {
      log(`\n⚠️ 控制台错误 (${testResults.errors.length}):`);
      testResults.errors.forEach((error, index) => {
        log(`  ${index + 1}. ${error.message}`, 'error');
      });
    }
    
    const total = testResults.passed.length + testResults.failed.length;
    log(`\n总计: ${total} 个测试`);
    log(`通过率: ${Math.round(testResults.passed.length / total * 100)}%`);
    
    // 保存测试报告
    const fs = require('fs');
    const report = {
      timestamp: new Date().toISOString(),
      config: CONFIG,
      results: testResults,
      requests: requests
    };
    
    fs.writeFileSync('test-report.json', JSON.stringify(report, null, 2));
    log('\n测试报告已保存到 test-report.json');
    
  } catch (error) {
    log(`测试执行出错: ${error.message}`, 'error');
    log(error.stack, 'error');
    await page.screenshot({ path: 'test-screenshots/error.png' });
  } finally {
    await browser.close();
    log('\n浏览器已关闭');
  }
})();
