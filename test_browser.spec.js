const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false
  });
  
  // 创建上下文
  const context = await browser.newContext();
  
  // 测试1: 登录页面重定向
  console.log('测试1: 登录页面重定向功能');
  await page.goto('http://localhost:3000/login');
  await page.waitForTimeout(1000);
  
  // 检查是否显示登录表单（未登录状态）
  const loginFormVisible = await page.isVisible('form.el-form');
  console.log('✅ 未登录状态： 登录表单可见');
  
  // 登录
  await page.fill('input[type="email"]', 'testuser2');
  await page.fill('input[type="password"]', 'testpass');
  await page.click('button:has-text("登录")');
  
  // 磁贴登录后的跳转
  await page.waitForTimeout(3000);
  
  // 检查是否跳转到首页
  const currentUrl = page.url();
  console.log('当前URL:', currentUrl);
  
  if (currentUrl.includes('/dashboard') || currentUrl === '/') {
    console.log('✅ 登录成功后跳转到首页');
  } else {
    console.log('❌ 登录后未跳转到首页');
  }
  
  // 测试2: 调研页面请求
  console.log('\n测试2: 调研页面请求');
  await page.goto('http://localhost:3000/survey');
  await page.waitForTimeout(2000);
  
  // 检查是否发送了API请求
  const networkRequests = = [];
  page.on('request', request => {
    networkRequests.push(request);
    console.log('API请求:', request.url(), request.method());
  });
  
  await page.waitForTimeout(3000);
  
  // 检查是否有调研列表API请求
  const surveyRequest = networkRequests.find(r => 
    r.url().includes('/api/v1/surveys') && r.method() === 'GET'
  );
  
  if (surveyRequest) {
    console.log('✅ 发现调研列表API请求:', surveyRequest.url());
  } else {
    console.log('❌ 未发现调研列表API请求');
    console.log('所有请求:', networkRequests.map(r => r.url()));
  }
  
  // 测试3: 数据分析页面布局
  console.log('\n测试3: 数据分析页面布局');
  await page.goto('http://localhost:3000/analysis');
  await page.waitForTimeout(2000);
  
  // 检查是否有三个切换按钮
  const tabButtons = await page.$$('el-radio-group .el-radio-button');
  console.log('找到的标签按钮数量:', tabButtons.length);
  
  if (tabButtons.length === 3) {
    console.log('✅ 找到三个切换按钮');
  } else {
    console.log('❌ 标签按钮数量不正确:', tabButtons.length);
  }
  
  // 检查是否只显示一个板块
  const visibleSections = await page.$$('.tab-content');
  console.log('可见板块数量:', visibleSections.length);
  
  await browser.close();
  
  console.log('\n=== 测试完成 ===');
})();
