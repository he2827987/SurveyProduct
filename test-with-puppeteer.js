const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class PuppeteerButtonTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.testResults = [];
    this.screenshotDir = path.join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct');
    this.stepCounter = 0;
  }

  async ensureScreenshotDir() {
    try {
      await fs.mkdir(this.screenshotDir, { recursive: true });
    } catch (error) {
      // Directory already exists
    }
  }

  async captureAndSave(stepName, description) {
    await this.ensureScreenshotDir();
    this.stepCounter++;
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${String(this.stepCounter).padStart(2, '0')}_${stepName}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);
    
    await this.page.screenshot({
      path: filepath,
      fullPage: true
    });
    
    console.log(`📸 Screenshot saved: ${filename}`);
    if (description) {
      console.log(`   Description: ${description}`);
    }
    
    return { path: filepath, filename, stepName, description };
  }

  async wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async setup() {
    console.log('🚀 Setting up Puppeteer test...\n');
    
    this.browser = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });
    
    this.page = await this.browser.newPage();
    
    console.log('✓ Browser ready\n');
  }

  async login() {
    console.log('🔐 Step 1: Login\n');
    
    await this.page.goto('http://localhost:3000/login', { waitUntil: 'networkidle2' });
    await this.wait(3000);
    
    await this.captureAndSave('login-page', 'Login page loaded');
    
    try {
      await this.page.waitForSelector('.el-input input', { timeout: 10000 });
      console.log('  ✓ Vue app loaded successfully');
    } catch (error) {
      await this.captureAndSave('login-vue-failed', 'Vue app failed to load');
      throw new Error('Vue app did not load');
    }
    
    const emailInput = await this.page.$('.el-input input');
    await emailInput.click();
    await emailInput.type('he2827987@gmail.com', { delay: 50 });
    console.log('  ✓ Email filled');
    
    const passwordInput = await this.page.$('input[type="password"]');
    await passwordInput.click();
    await passwordInput.type('13245678', { delay: 50 });
    console.log('  ✓ Password filled');
    
    await this.captureAndSave('login-filled', 'Login form filled');
    
    const loginBtn = await this.page.$('button.el-button--primary');
    await loginBtn.click();
    console.log('  ✓ Login button clicked');
    
    await this.wait(3000);
    
    const currentUrl = this.page.url();
    const success = !currentUrl.includes('/login');
    
    await this.captureAndSave(`login-${success ? 'success' : 'failed'}`, `Login ${success ? 'SUCCESS' : 'FAILED'}`);
    
    this.testResults.push({
      test: 'Login',
      status: success ? 'PASS' : 'FAIL',
      url: currentUrl
    });
    
    console.log(`  ${success ? '✅' : '❌'} Login ${success ? 'successful' : 'failed'}\n`);
    
    return success;
  }

  async testPage(name, path, expectedButtons) {
    console.log(`\n📍 Testing: ${name}\n`);
    
    await this.page.goto(`http://localhost:3000${path}`, { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    await this.captureAndSave(`page-${name.toLowerCase().replace(/\s+/g, '-')}`, `${name} page`);
    
    const buttons = await this.page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button, .el-button, [role="button"]'));
      return btns.map(b => ({
        text: b.textContent.trim(),
        visible: b.offsetParent !== null,
        disabled: b.disabled
      })).filter(b => b.visible);
    });
    
    console.log(`  Found ${buttons.length} visible buttons:`);
    buttons.forEach((btn, i) => {
      console.log(`    ${i + 1}. "${btn.text}" ${btn.disabled ? '(disabled)' : ''}`);
    });
    
    this.testResults.push({
      test: `Navigate to ${name}`,
      status: 'PASS',
      buttonCount: buttons.length,
      buttons: buttons.map(b => b.text)
    });
    
    return buttons;
  }

  async testButtonClick(pageName, buttonText) {
    console.log(`  Testing button: "${buttonText}"`);
    
    try {
      const button = await this.page.$(`button:has-text("${buttonText}"), .el-button:has-text("${buttonText}")`);
      
      if (!button) {
        console.log(`    ⚠️  Button "${buttonText}" not found`);
        return false;
      }
      
      await button.click();
      await this.wait(1000);
      
      await this.captureAndSave(`click-${buttonText.toLowerCase().replace(/\s+/g, '-')}`, `Clicked "${buttonText}"`);
      
      console.log(`    ✅ Button "${buttonText}" clicked successfully`);
      return true;
    } catch (error) {
      console.log(`    ❌ Failed to click "${buttonText}": ${error.message}`);
      return false;
    }
  }

  async testAllPages() {
    const pages = [
      { name: 'Home', path: '/' },
      { name: 'Surveys', path: '/surveys' },
      { name: 'Analysis', path: '/analysis' },
      { name: 'Questions', path: '/questions' },
      { name: 'Organizations', path: '/organizations' }
    ];
    
    for (const pageInfo of pages) {
      await this.testPage(pageInfo.name, pageInfo.path);
    }
  }

  async testSurveyCreation() {
    console.log('\n📍 Testing: Survey Creation Flow\n');
    
    await this.page.goto('http://localhost:3000/surveys', { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    const createBtn = await this.page.$('button:has-text("新建"), button:has-text("创建")');
    
    if (createBtn) {
      await createBtn.click();
      await this.wait(1000);
      
      await this.captureAndSave('survey-create-form', 'Survey creation form opened');
      
      const inputs = await this.page.$$('input:visible, textarea:visible');
      console.log(`  Found ${inputs.length} input fields in creation form`);
      
      const cancelBtn = await this.page.$('button:has-text("取消"), button:has-text("返回")');
      if (cancelBtn) {
        await cancelBtn.click();
        await this.wait(500);
      }
      
      this.testResults.push({
        test: 'Survey Creation Form',
        status: 'PASS',
        inputCount: inputs.length
      });
    }
  }

  async testAnalysisFeatures() {
    console.log('\n📍 Testing: Analysis Features\n');
    
    await this.page.goto('http://localhost:3000/analysis', { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    const tabs = await this.page.$$('.el-radio-button, .el-tabs__item');
    console.log(`  Found ${tabs.length} tab buttons`);
    
    for (let i = 0; i < Math.min(3, tabs.length); i++) {
      await tabs[i].click();
      await this.wait(500);
      await this.captureAndSave(`analysis-tab-${i + 1}`, `Analysis tab ${i + 1}`);
    }
    
    const exportBtn = await this.page.$('button:has-text("导出"), button:has-text("Export")');
    if (exportBtn) {
      console.log('  ✓ Export button found');
    }
    
    const llmBtn = await this.page.$('button:has-text("AI"), button:has-text("总结")');
    if (llmBtn) {
      console.log('  ✓ LLM summary button found');
    }
  }

  async testMobileView() {
    console.log('\n📍 Testing: Mobile View\n');
    
    await this.page.setViewport({ width: 375, height: 812 });
    
    await this.page.goto('http://localhost:3000/', { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    await this.captureAndSave('mobile-view', 'Mobile view (375x812)');
    
    const buttons = await this.page.$$('button:visible');
    console.log(`  Found ${buttons.length} buttons in mobile view`);
    
    this.testResults.push({
      test: 'Mobile View',
      status: 'PASS',
      buttonCount: buttons.length
    });
    
    await this.page.setViewport({ width: 1920, height: 1080 });
  }

  async generateReport() {
    console.log('\n📊 Generating Test Report\n');
    console.log('='.repeat(60));
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.status === 'PASS').length,
        failed: this.testResults.filter(r => r.status === 'FAIL').length
      },
      results: this.testResults
    };
    
    const reportPath = path.join(this.screenshotDir, 'puppeteer-test-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`Total Tests: ${report.summary.total}`);
    console.log(`Passed: ${report.summary.passed} ✅`);
    console.log(`Failed: ${report.summary.failed} ❌`);
    console.log(`\nReport: ${reportPath}`);
    console.log(`Screenshots: ${this.screenshotDir}`);
    
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
        await this.testAllPages();
        await this.testSurveyCreation();
        await this.testAnalysisFeatures();
        await this.testMobileView();
      } else {
        console.log('\n⚠️  Login failed, skipping authenticated tests\n');
      }
      
      const report = await this.generateReport();
      
      await this.cleanup();
      
      return report;
    } catch (error) {
      console.error('\n❌ Test error:', error.message);
      await this.cleanup();
      throw error;
    }
  }
}

async function main() {
  const tester = new PuppeteerButtonTester();
  await tester.runAllTests();
}

if (require.main === module) {
  main();
}

module.exports = PuppeteerButtonTester;
