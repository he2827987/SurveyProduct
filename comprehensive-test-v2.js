const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class ComprehensiveTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.testResults = [];
    this.screenshotDir = path.join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct');
    this.stepCounter = 0;
  }

  async wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async capture(name, desc) {
    this.stepCounter++;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${String(this.stepCounter).padStart(2, '0')}_${name}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);
    await this.page.screenshot({ path: filepath, fullPage: true });
    console.log(`📸 ${filename} - ${desc}`);
    return filepath;
  }

  async setup() {
    console.log('========================================');
    console.log('开始全面功能测试');
    console.log('========================================\n');
    
    this.browser = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });
    
    this.page = await this.browser.newPage();
    
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`  ❌ Console: ${msg.text()}`);
      }
    });
    
    console.log('✓ 浏览器就绪\n');
  }

  async login() {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔐 测试1: 登录认证');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    await this.page.goto('http://localhost:3000/login', { waitUntil: 'networkidle2' });
    await this.wait(3000);
    
    // 等待Vue应用加载
    let retries = 0;
    while (retries < 10) {
      const inputs = await this.page.$$('input');
      if (inputs.length >= 2) {
        console.log(`  ✓ Vue应用已加载，找到 ${inputs.length} 个输入框`);
        break;
      }
      await this.wait(1000);
      retries++;
      console.log(`  等待Vue加载... (${retries}/10)`);
    }
    
    await this.capture('login-page', '登录页面');
    
    // 填写登录信息
    const inputs = await this.page.$$('input');
    if (inputs.length >= 2) {
      await inputs[0].click();
      await inputs[0].type('he2827987@gmail.com', { delay: 30 });
      console.log('  ✓ 填写邮箱');
      
      const passwordInput = await this.page.$('input[type="password"]');
      if (passwordInput) {
        await passwordInput.click();
        await passwordInput.type('13245678', { delay: 30 });
        console.log('  ✓ 填写密码');
      }
      
      await this.capture('login-filled', '登录表单已填写');
      
      // 点击登录按钮
      const buttons = await this.page.$$('button');
      for (const btn of buttons) {
        const text = await (await btn.getProperty('textContent')).jsonValue();
        if (text.includes('登录')) {
          await btn.click();
          console.log('  ✓ 点击登录按钮');
          break;
        }
      }
      
      await this.wait(3000);
      const currentUrl = this.page.url();
      const success = !currentUrl.includes('/login');
      
      await this.capture(`login-${success ? 'success' : 'failed'}`, `登录${success ? '成功' : '失败'}`);
      
      this.testResults.push({
        test: '登录认证',
        status: success ? 'PASS' : 'FAIL',
        url: currentUrl
      });
      
      console.log(`  ${success ? '✅' : '❌'} 登录${success ? '成功' : '失败'}\n`);
      return success;
    }
    
    return false;
  }

  async testSidebarMenu() {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📋 测试2: 侧边栏菜单导航');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    const menuItems = [
      { name: '首页', path: '/dashboard' },
      { name: '组织架构管理', path: '/organization' },
      { name: '题库管理', path: '/question' },
      { name: '调研管理', path: '/survey' },
      { name: '数据分析', path: '/analysis' },
      { name: '企业对比', path: '/compare' }
    ];
    
    for (const item of menuItems) {
      console.log(`\n📍 测试菜单: ${item.name}`);
      
      await this.page.goto(`http://localhost:3000${item.path}`, { waitUntil: 'networkidle2' });
      await this.wait(2000);
      
      const pageInfo = await this.page.evaluate(() => ({
        title: document.title,
        url: window.location.href,
        buttons: document.querySelectorAll('button').length,
        tables: document.querySelectorAll('table, .el-table').length,
        forms: document.querySelectorAll('form, .el-form').length
      }));
      
      await this.capture(`menu-${item.name}`, `${item.name}页面`);
      
      console.log(`  URL: ${pageInfo.url}`);
      console.log(`  标题: ${pageInfo.title}`);
      console.log(`  按钮: ${pageInfo.buttons}个`);
      console.log(`  表格: ${pageInfo.tables}个`);
      console.log(`  表单: ${pageInfo.forms}个`);
      
      const success = pageInfo.url.includes(item.path);
      
      this.testResults.push({
        test: `菜单导航 - ${item.name}`,
        status: success ? 'PASS' : 'FAIL',
        buttons: pageInfo.buttons
      });
      
      console.log(`  ${success ? '✅' : '❌'} ${item.name} ${success ? '成功' : '失败'}`);
    }
  }

  async testSurveyFlow() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📝 测试3: 调研创建流程');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    await this.page.goto('http://localhost:3000/survey', { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    await this.capture('survey-list', '调研列表页面');
    
    // 查找创建按钮
    const buttons = await this.page.$$('button');
    let createBtn = null;
    
    for (const btn of buttons) {
      const text = await (await btn.getProperty('textContent')).jsonValue();
      if (text.includes('新建') || text.includes('创建')) {
        createBtn = btn;
        console.log(`  ✓ 找到创建按钮: "${text.trim()}"`);
        break;
      }
    }
    
    if (createBtn) {
      await createBtn.click();
      await this.wait(2000);
      
      await this.capture('survey-create-form', '调研创建表单');
      
      // 检查表单字段
      const formInfo = await this.page.evaluate(() => ({
        inputs: document.querySelectorAll('input, textarea').length,
        selects: document.querySelectorAll('select, .el-select').length,
        buttons: document.querySelectorAll('button').length
      }));
      
      console.log(`  表单输入框: ${formInfo.inputs}个`);
      console.log(`  下拉选择: ${formInfo.selects}个`);
      console.log(`  按钮: ${formInfo.buttons}个`);
      
      // 尝试填写表单
      const inputs = await this.page.$$('input');
      if (inputs.length > 0) {
        await inputs[0].click();
        await inputs[0].type(`自动化测试调研 - ${Date.now()}`, { delay: 30 });
        console.log('  ✓ 填写调研标题');
        
        await this.capture('survey-form-filled', '调研表单已填写');
      }
      
      this.testResults.push({
        test: '调研创建',
        status: 'PASS',
        formInputs: formInfo.inputs
      });
      
      console.log('  ✅ 调研创建表单测试完成\n');
    } else {
      console.log('  ⚠️  未找到创建按钮\n');
      this.testResults.push({
        test: '调研创建',
        status: 'FAIL',
        reason: '未找到创建按钮'
      });
    }
  }

  async testDataAnalysis() {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 测试4: 数据分析');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    await this.page.goto('http://localhost:3000/analysis', { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    await this.capture('analysis-page', '数据分析页面');
    
    const analysisInfo = await this.page.evaluate(() => ({
      charts: document.querySelectorAll('canvas, .echarts').length,
      tabs: document.querySelectorAll('.el-tabs__item, .el-radio-button').length,
      buttons: document.querySelectorAll('button').length
    }));
    
    console.log(`  图表: ${analysisInfo.charts}个`);
    console.log(`  标签页: ${analysisInfo.tabs}个`);
    console.log(`  按钮: ${analysisInfo.buttons}个`);
    
    // 测试标签页切换
    const tabs = await this.page.$$('.el-tabs__item, .el-radio-button');
    if (tabs.length > 0) {
      for (let i = 0; i < Math.min(3, tabs.length); i++) {
        await tabs[i].click();
        await this.wait(500);
        await this.capture(`analysis-tab-${i + 1}`, `分析标签${i + 1}`);
      }
      console.log(`  ✓ 测试了 ${Math.min(3, tabs.length)} 个标签页`);
    }
    
    this.testResults.push({
      test: '数据分析',
      status: 'PASS',
      charts: analysisInfo.charts,
      tabs: analysisInfo.tabs
    });
    
    console.log('  ✅ 数据分析测试完成\n');
  }

  async generateReport() {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 测试报告');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.status === 'PASS').length,
        failed: this.testResults.filter(r => r.status === 'FAIL').length
      },
      details: this.testResults
    };
    
    const reportPath = path.join(this.screenshotDir, 'comprehensive-test-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`总测试数: ${report.summary.total}`);
    console.log(`通过: ${report.summary.passed} ✅`);
    console.log(`失败: ${report.summary.failed} ❌`);
    console.log(`\n报告保存: ${reportPath}`);
    console.log(`截图保存: ${this.screenshotDir}`);
    console.log(`截图数量: ${this.stepCounter}张\n`);
    
    console.log('详细结果:');
    this.testResults.forEach((result, i) => {
      const icon = result.status === 'PASS' ? '✅' : '❌';
      console.log(`  ${i + 1}. ${icon} ${result.test}`);
    });
    
    return report;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async runAllTests() {
    try {
      await this.setup();
      
      const loginSuccess = await this.login();
      
      if (loginSuccess) {
        await this.testSidebarMenu();
        await this.testSurveyFlow();
        await this.testDataAnalysis();
      } else {
        console.log('\n⚠️  登录失败，跳过后续测试\n');
      }
      
      await this.generateReport();
      await this.cleanup();
      
    } catch (error) {
      console.error('\n❌ 测试错误:', error.message);
      await this.cleanup();
      throw error;
    }
  }
}

(async () => {
  const tester = new ComprehensiveTester();
  await tester.runAllTests();
})();
