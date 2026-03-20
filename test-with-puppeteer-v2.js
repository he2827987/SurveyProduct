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
    } catch (error) {}
  }

  async captureAndSave(stepName, description) {
    await this.ensureScreenshotDir();
    this.stepCounter++;
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${String(this.stepCounter).padStart(2, '0')}_${stepName}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);
    
    await this.page.screenshot({ path: filepath, fullPage: true });
    
    console.log(`📸 ${filename}`);
    if (description) console.log(`   ${description}`);
    
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
    
    // Log console errors
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('  ❌ Console error:', msg.text());
      }
    });
    
    // Log page errors
    this.page.on('pageerror', error => {
      console.log('  ❌ Page error:', error.message);
    });
    
    console.log('✓ Browser ready\n');
  }

  async login() {
    console.log('🔐 Step 1: Login\n');
    
    console.log('  Navigating to login page...');
    await this.page.goto('http://localhost:3000/login', { waitUntil: 'networkidle2', timeout: 30000 });
    
    console.log('  Waiting 5 seconds for Vue to load...');
    await this.wait(5000);
    
    await this.captureAndSave('login-after-wait', 'Login page after 5s wait');
    
    // Check #app content
    const appContent = await this.page.evaluate(() => {
      const app = document.querySelector('#app');
      return app ? {
        exists: true,
        hasChildren: app.children.length > 0,
        innerHTML: app.innerHTML.substring(0, 300),
        childCount: app.children.length
      } : { exists: false };
    });
    
    console.log('  #app status:', JSON.stringify(appContent, null, 2));
    
    // Try to find any input
    const allInputs = await this.page.$$('input');
    console.log(`  Total inputs found: ${allInputs.length}`);
    
    if (allInputs.length === 0) {
      await this.captureAndSave('no-inputs-found', 'No input fields found');
      throw new Error('No input fields found - Vue app may not have loaded');
    }
    
    // Fill first visible input (email)
    for (const input of allInputs) {
      const isVisible = await input.boundingBox();
      if (isVisible) {
        await input.click();
        await input.type('he2827987@gmail.com', { delay: 50 });
        console.log('  ✓ Email filled in first visible input');
        break;
      }
    }
    
    // Find password input
    const passwordInputs = await this.page.$$('input[type="password"]');
    if (passwordInputs.length > 0) {
      await passwordInputs[0].click();
      await passwordInputs[0].type('13245678', { delay: 50 });
      console.log('  ✓ Password filled');
    } else {
      console.log('  ⚠️  No password input found');
    }
    
    await this.captureAndSave('login-form-filled', 'Login form filled');
    
    // Find login button
    const buttons = await this.page.$$('button');
    console.log(`  Found ${buttons.length} buttons`);
    
    let loginBtn = null;
    for (const btn of buttons) {
      const text = await (await btn.getProperty('textContent')).jsonValue();
      if (text.includes('登录') || text.includes('Login')) {
        loginBtn = btn;
        console.log(`  Found login button: "${text.trim()}"`);
        break;
      }
    }
    
    if (!loginBtn) {
      throw new Error('Login button not found');
    }
    
    await loginBtn.click();
    console.log('  ✓ Login button clicked');
    
    await this.wait(3000);
    
    const currentUrl = this.page.url();
    const success = !currentUrl.includes('/login');
    
    await this.captureAndSave(`login-result-${success ? 'success' : 'failed'}`, `Login ${success ? 'SUCCESS' : 'FAILED'}`);
    
    this.testResults.push({
      test: 'Login',
      status: success ? 'PASS' : 'FAIL',
      url: currentUrl
    });
    
    console.log(`  ${success ? '✅' : '❌'} Login ${success ? 'successful' : 'failed'}: ${currentUrl}\n`);
    
    return success;
  }

  async testPage(name, url) {
    console.log(`\n📍 Testing: ${name}\n`);
    
    await this.page.goto(`http://localhost:3000${url}`, { waitUntil: 'networkidle2' });
    await this.wait(2000);
    
    await this.captureAndSave(`page-${name.toLowerCase()}`, `${name} page`);
    
    const pageInfo = await this.page.evaluate(() => ({
      title: document.title,
      url: window.location.href,
      buttons: Array.from(document.querySelectorAll('button')).map(b => ({
        text: b.textContent.trim(),
        visible: b.offsetParent !== null
      })).filter(b => b.visible)
    }));
    
    console.log(`  Title: ${pageInfo.title}`);
    console.log(`  Buttons: ${pageInfo.buttons.length}`);
    pageInfo.buttons.forEach((btn, i) => {
      console.log(`    ${i + 1}. "${btn.text}"`);
    });
    
    this.testResults.push({
      test: name,
      status: 'PASS',
      buttonCount: pageInfo.buttons.length
    });
  }

  async generateReport() {
    console.log('\n📊 Test Report\n');
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
    
    const reportPath = path.join(this.screenshotDir, 'puppeteer-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`Total: ${report.summary.total}`);
    console.log(`Passed: ${report.summary.passed} ✅`);
    console.log(`Failed: ${report.summary.failed} ❌`);
    console.log(`\nReport: ${reportPath}`);
    
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
        await this.testPage('Home', '/');
        await this.testPage('Surveys', '/surveys');
        await this.testPage('Analysis', '/analysis');
        await this.testPage('Questions', '/questions');
      }
      
      await this.generateReport();
      await this.cleanup();
    } catch (error) {
      console.error('\n❌ Error:', error.message);
      await this.cleanup();
      throw error;
    }
  }
}

(async () => {
  const tester = new PuppeteerButtonTester();
  await tester.runAllTests();
})();
