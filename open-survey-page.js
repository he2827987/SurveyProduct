const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 正在启动浏览器...\n');
  
  const browser = await puppeteer.launch({
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--start-maximized'
    ],
    defaultViewport: null
  });
  
  const page = await browser.newPage();
  
  // 监听控制台输出
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'log') {
      console.log(`[浏览器日志] ${text}`);
    } else if (type === 'error') {
      console.log(`[浏览器错误] ❌ ${text}`);
    } else if (type === 'warning') {
      console.log(`[浏览器警告] ⚠️  ${text}`);
    }
  });
  
  // 监听页面错误
  page.on('pageerror', error => {
    console.log(`[页面错误] ❌ ${error.message}`);
  });
  
  // 监听请求失败
  page.on('requestfailed', request => {
    console.log(`[请求失败] ❌ ${request.url()} - ${request.failure().errorText}`);
  });
  
  console.log('📍 正在访问登录页面...');
  console.log('   URL: http://localhost:3000/login\n');
  
  await page.goto('http://localhost:3000/login', {
    waitUntil: 'networkidle2',
    timeout: 30000
  });
  
  // 等待页面加载
  console.log('⏳ 等待页面加载...\n');
  await new Promise(r => setTimeout(r, 5000));
  
  // 检查Vue应用状态
  const appStatus = await page.evaluate(() => {
    const app = document.querySelector('#app');
    return {
      exists: !!app,
      hasChildren: app ? app.children.length > 0 : false,
      innerHTML: app ? app.innerHTML.substring(0, 200) : '',
      vueMounted: window.__VUE_APP_MOUNTED__
    };
  });
  
  console.log('🔍 Vue应用状态:');
  console.log(`   #app元素存在: ${appStatus.exists ? '✅' : '❌'}`);
  console.log(`   #app有子元素: ${appStatus.hasChildren ? '✅' : '❌'}`);
  console.log(`   Vue已挂载: ${appStatus.vueMounted ? '✅' : '❌'}`);
  console.log(`   #app内容: ${appStatus.innerHTML.substring(0, 100)}...\n`);
  
  // 等待输入框出现
  console.log('⏳ 等待登录表单加载...');
  try {
    await page.waitForSelector('input', { timeout: 15000 });
    console.log('   ✅ 找到输入框\n');
  } catch (error) {
    console.log('   ❌ 未找到输入框，继续等待...\n');
  }
  
  // 检查所有输入框
  const inputs = await page.$$('input');
  console.log(`📋 页面输入框数量: ${inputs.length}`);
  
  if (inputs.length > 0) {
    console.log('\n✅ Vue应用已成功加载！');
    console.log('\n📝 正在填写登录信息...');
    
    // 填写邮箱
    await inputs[0].click();
    await inputs[0].type('he2827987@gmail.com', { delay: 30 });
    console.log('   ✅ 邮箱已填写');
    
    // 查找密码输入框
    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      await passwordInput.click();
      await passwordInput.type('13245678', { delay: 30 });
      console.log('   ✅ 密码已填写');
    }
    
    // 截图
    await page.screenshot({ path: 'survey-page-login.png', fullPage: true });
    console.log('   📸 截图已保存: survey-page-login.png\n');
    
    // 点击登录按钮
    console.log('🖱️  点击登录按钮...');
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await (await btn.getProperty('textContent')).jsonValue();
      if (text.includes('登录')) {
        await btn.click();
        console.log('   ✅ 登录按钮已点击\n');
        break;
      }
    }
    
    // 等待登录完成
    console.log('⏳ 等待登录完成...');
    await new Promise(r => setTimeout(r, 3000));
    
    const currentUrl = page.url();
    console.log(`   当前URL: ${currentUrl}`);
    
    if (!currentUrl.includes('/login')) {
      console.log('   ✅ 登录成功！\n');
      
      // 访问调研管理页面
      console.log('📍 正在访问调研管理页面...');
      console.log('   URL: http://localhost:3000/survey\n');
      
      await page.goto('http://localhost:3000/survey', {
        waitUntil: 'networkidle2',
        timeout: 30000
      });
      
      await new Promise(r => setTimeout(r, 3000));
      
      // 检查页面状态
      const surveyStatus = await page.evaluate(() => ({
        title: document.title,
        url: window.location.href,
        hasTable: document.querySelector('table, .el-table') !== null,
        hasButtons: document.querySelectorAll('button').length > 0,
        buttons: Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()).slice(0, 10)
      }));
      
      console.log('🔍 调研管理页面状态:');
      console.log(`   标题: ${surveyStatus.title}`);
      console.log(`   URL: ${surveyStatus.url}`);
      console.log(`   有表格: ${surveyStatus.hasTable ? '✅' : '❌'}`);
      console.log(`   有按钮: ${surveyStatus.hasButtons ? '✅' : '❌'}`);
      console.log(`   按钮列表: ${surveyStatus.buttons.join(', ')}\n`);
      
      // 截图
      await page.screenshot({ path: 'survey-page-management.png', fullPage: true });
      console.log('📸 截图已保存: survey-page-management.png\n');
      
      if (surveyStatus.hasTable || surveyStatus.hasButtons) {
        console.log('✅ 调研管理页面加载成功！');
        console.log('\n💡 浏览器窗口将保持打开状态，您可以手动操作');
        console.log('💡 完成测试后，按 Ctrl+C 关闭\n');
      } else {
        console.log('⚠️  页面可能未完全加载，请手动检查');
      }
      
    } else {
      console.log('   ❌ 登录失败，仍在登录页面\n');
    }
    
  } else {
    console.log('\n❌ Vue应用未正确加载');
    console.log('💡 浏览器窗口将保持打开状态，请手动检查');
    console.log('💡 您可以手动刷新页面或查看控制台错误\n');
  }
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🌐 浏览器窗口保持打开');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  
  // 保持浏览器打开
  await new Promise(() => {});
  
})();
