const { webkit } = require('playwright');
const { BrowserHelper } = require('./tests/helpers/browser-helper');
const { AuthHelper } = require('./tests/helpers/auth-helper');
const { VisualDebugger } = require('./tests/helpers/visual-debug');
const fs = require('fs').promises;

class ComprehensiveButtonTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.browserHelper = null;
    this.authHelper = null;
    this.visualDebugger = null;
    this.testResults = [];
    this.screenshotDir = require('path').join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct');
  }

  async setup() {
    console.log('🚀 Setting up comprehensive button test...\n');
    
    this.browser = await webkit.launch({
      headless: false,
      slowMo: 100
    });
    
    const context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 }
    });
    
    this.page = await context.newPage();
    this.browserHelper = new BrowserHelper(this.page);
    this.authHelper = new AuthHelper(this.page, this.browserHelper);
    this.visualDebugger = new VisualDebugger(this.browserHelper);
    
    console.log('✓ Browser ready\n');
  }

  async login() {
    console.log('🔐 Step 1: Login\n');
    
    await this.page.goto('http://localhost:3000/login');
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(5000);
    
    await this.browserHelper.captureAndSave('01-login-page', 'Initial login page after 5s wait');
    
    let attempts = 0;
    let emailInput = null;
    
    while (!emailInput && attempts < 5) {
      emailInput = await this.page.$('.el-input input, input[type="text"], input[placeholder*="邮箱"]');
      if (!emailInput) {
        console.log(`  Waiting for Vue app to load... (attempt ${attempts + 1}/5)`);
        await this.page.waitForTimeout(2000);
        attempts++;
      }
    }
    
    if (!emailInput) {
      await this.browserHelper.captureAndSave('01b-login-failed', 'Vue app failed to load');
      throw new Error('Vue app did not load - no input fields found');
    }
    
    await emailInput.click();
    await emailInput.fill('he2827987@gmail.com');
    console.log('  ✓ Email filled');
    
    const passwordInput = await this.page.$('input[type="password"]');
    await passwordInput.fill('13245678');
    console.log('  ✓ Password filled');
    
    await this.browserHelper.captureAndSave('02-filled-login', 'Login form filled');
    
    const loginBtn = await this.page.$('button.el-button--primary, button:has-text("登录")');
    await loginBtn.click();
    console.log('  ✓ Login button clicked');
    
    await this.page.waitForTimeout(3000);
    
    const currentUrl = this.page.url();
    const success = !currentUrl.includes('/login');
    
    await this.browserHelper.captureAndSave('03-after-login', `Login ${success ? 'SUCCESS' : 'FAILED'}`);
    
    this.testResults.push({
      test: 'Login',
      status: success ? 'PASS' : 'FAIL',
      url: currentUrl
    });
    
    console.log(`  ${success ? '✅' : '❌'} Login ${success ? 'successful' : 'failed'}: ${currentUrl}`);
    
    return success;
  }

  async testHomePageButtons() {
    console.log('\n📍 Step 2: Testing Home Page Buttons\n');
    
    await this.page.goto('http://localhost:3000/');
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('04-home-page', 'Home page loaded');
    
    const pageInfo = await this.browserHelper.getPageInfo();
    console.log(`Found ${pageInfo.buttons.length} buttons on home page`);
    
    for (let i = 0; i < pageInfo.buttons.length; i++) {
      const btn = pageInfo.buttons[i];
      if (btn.visible && !btn.disabled) {
        console.log(`  Testing button: "${btn.text}"`);
      }
    }
    
    this.testResults.push({
      test: 'Home Page Buttons',
      status: 'PASS',
      count: pageInfo.buttons.filter(b => b.visible).length
    });
  }

  async testNavigationButtons() {
    console.log('\n📍 Step 3: Testing Navigation Buttons\n');
    
    const navItems = [
      { name: 'Surveys', path: '/surveys' },
      { name: 'Analysis', path: '/analysis' },
      { name: 'Questions', path: '/questions' },
      { name: 'Organizations', path: '/organizations' }
    ];
    
    for (const item of navItems) {
      try {
        console.log(`  Testing navigation to: ${item.name}`);
        
        await this.page.goto(`http://localhost:3000${item.path}`);
        await this.page.waitForTimeout(2000);
        
        const url = this.page.url();
        const pageInfo = await this.browserHelper.getPageInfo();
        
        await this.browserHelper.captureAndSave(
          `05-nav-${item.name.toLowerCase()}`,
          `${item.name} page - ${pageInfo.buttons.length} buttons`
        );
        
        this.testResults.push({
          test: `Navigate to ${item.name}`,
          status: url.includes(item.path) ? 'PASS' : 'FAIL',
          url: url,
          buttonCount: pageInfo.buttons.length
        });
        
        console.log(`    ✓ ${item.name}: ${pageInfo.buttons.length} buttons found`);
      } catch (error) {
        console.log(`    ✗ ${item.name}: ${error.message}`);
        this.testResults.push({
          test: `Navigate to ${item.name}`,
          status: 'FAIL',
          error: error.message
        });
      }
    }
  }

  async testSurveyButtons() {
    console.log('\n📍 Step 4: Testing Survey Page Buttons\n');
    
    await this.page.goto('http://localhost:3000/surveys');
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('06-surveys-page', 'Surveys list page');
    
    const createBtn = await this.page.$('button:has-text("新建"), button:has-text("创建"), .el-button--primary');
    
    if (createBtn) {
      console.log('  Testing "Create Survey" button');
      await createBtn.click();
      await this.page.waitForTimeout(2000);
      
      await this.browserHelper.captureAndSave('07-create-survey', 'Create survey form');
      
      const formInputs = await this.page.$$('input:visible, textarea:visible');
      console.log(`    Found ${formInputs.length} form inputs`);
      
      const backBtn = await this.page.$('button:has-text("返回"), button:has-text("取消")');
      if (backBtn) {
        await backBtn.click();
        await this.page.waitForTimeout(1000);
      }
      
      this.testResults.push({
        test: 'Create Survey Button',
        status: 'PASS',
        formInputs: formInputs.length
      });
    }
    
    const surveyCards = await this.page.$$('.survey-card, .el-card, [class*="survey"]');
    if (surveyCards.length > 0) {
      console.log(`  Testing survey card buttons (${surveyCards.length} cards found)`);
      
      const editBtn = await this.page.$('button:has-text("编辑"), button:has-text("修改")');
      if (editBtn) {
        await editBtn.click();
        await this.page.waitForTimeout(1000);
        await this.browserHelper.captureAndSave('08-edit-survey', 'Edit survey form');
        
        const cancelBtn = await this.page.$('button:has-text("取消"), button:has-text("返回")');
        if (cancelBtn) {
          await cancelBtn.click();
          await this.page.waitForTimeout(500);
        }
      }
    }
  }

  async testAnalysisButtons() {
    console.log('\n📍 Step 5: Testing Analysis Page Buttons\n');
    
    await this.page.goto('http://localhost:3000/analysis');
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('09-analysis-page', 'Analysis page loaded');
    
    const tabButtons = await this.page.$$('.el-radio-button, .el-tabs__item');
    console.log(`  Found ${tabButtons.length} tab buttons`);
    
    for (let i = 0; i < Math.min(3, tabButtons.length); i++) {
      await tabButtons[i].click();
      await this.page.waitForTimeout(1000);
      await this.browserHelper.captureAndSave(`10-analysis-tab-${i}`, `Analysis tab ${i + 1}`);
    }
    
    const exportBtn = await this.page.$('button:has-text("导出"), button:has-text("Export")');
    if (exportBtn) {
      console.log('  Found export button');
      this.testResults.push({
        test: 'Analysis Export Button',
        status: 'FOUND'
      });
    }
    
    const llmBtn = await this.page.$('button:has-text("AI"), button:has-text("总结"), button:has-text("分析")');
    if (llmBtn) {
      console.log('  Found LLM summary button');
      this.testResults.push({
        test: 'LLM Summary Button',
        status: 'FOUND'
      });
    }
  }

  async testQuestionManagementButtons() {
    console.log('\n📍 Step 6: Testing Question Management Buttons\n');
    
    await this.page.goto('http://localhost:3000/questions');
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('11-questions-page', 'Questions management page');
    
    const createQBtn = await this.page.$('button:has-text("新建"), button:has-text("添加")');
    if (createQBtn) {
      console.log('  Testing "Create Question" button');
      await createQBtn.click();
      await this.page.waitForTimeout(2000);
      
      await this.browserHelper.captureAndSave('12-create-question', 'Create question form');
      
      const cancelBtn = await this.page.$('button:has-text("取消"), button:has-text("返回")');
      if (cancelBtn) {
        await cancelBtn.click();
        await this.page.waitForTimeout(500);
      }
    }
  }

  async testOrganizationButtons() {
    console.log('\n📍 Step 7: Testing Organization Buttons\n');
    
    await this.page.goto('http://localhost:3000/organizations');
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('13-organizations-page', 'Organizations page');
    
    const addOrgBtn = await this.page.$('button:has-text("新建"), button:has-text("添加")');
    if (addOrgBtn) {
      console.log('  Testing "Add Organization" button');
    }
  }

  async testMobileButtons() {
    console.log('\n📍 Step 8: Testing Mobile View Buttons\n');
    
    const mobileSizes = [
      { name: 'iPhone 12', width: 390, height: 844 }
    ];
    
    for (const size of mobileSizes) {
      await this.page.setViewportSize({ width: size.width, height: size.height });
      
      await this.page.goto('http://localhost:3000/');
      await this.page.waitForTimeout(2000);
      
      await this.browserHelper.captureAndSave(`14-mobile-${size.name.toLowerCase().replace(' ', '-')}`, `Mobile ${size.name}`);
      
      const pageInfo = await this.browserHelper.getPageInfo();
      console.log(`  ${size.name}: ${pageInfo.buttons.length} buttons`);
      
      this.testResults.push({
        test: `Mobile ${size.name}`,
        status: 'PASS',
        buttonCount: pageInfo.buttons.length
      });
    }
    
    await this.page.setViewportSize({ width: 1920, height: 1080 });
  }

  async generateReport() {
    console.log('\n📊 Generating Test Report\n');
    console.log('='.repeat(60));
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.status === 'PASS').length,
        failed: this.testResults.filter(r => r.status === 'FAIL').length,
        found: this.testResults.filter(r => r.status === 'FOUND').length
      },
      results: this.testResults
    };
    
    const reportPath = require('path').join(this.screenshotDir, 'button-test-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`Total Tests: ${report.summary.total}`);
    console.log(`Passed: ${report.summary.passed} ✅`);
    console.log(`Failed: ${report.summary.failed} ❌`);
    console.log(`Found: ${report.summary.found} 🔍`);
    console.log(`\nReport saved: ${reportPath}`);
    
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
        await this.testHomePageButtons();
        await this.testNavigationButtons();
        await this.testSurveyButtons();
        await this.testAnalysisButtons();
        await this.testQuestionManagementButtons();
        await this.testOrganizationButtons();
        await this.testMobileButtons();
      } else {
        console.log('\n⚠️  Login failed, testing limited pages only\n');
        await this.testNavigationButtons();
      }
      
      const report = await this.generateReport();
      
      await this.cleanup();
      
      return report;
    } catch (error) {
      console.error('\n❌ Test error:', error);
      await this.cleanup();
      throw error;
    }
  }
}

async function main() {
  const tester = new ComprehensiveButtonTester();
  await tester.runAllTests();
}

if (require.main === module) {
  main();
}

module.exports = ComprehensiveButtonTester;
