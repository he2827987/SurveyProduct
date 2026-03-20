const { chromium } = require('playwright');
const { BrowserHelper } = require('./tests/helpers/browser-helper');
const { AuthHelper } = require('./tests/helpers/auth-helper');
const { VisualDebugger } = require('./tests/helpers/visual-debug');
const fs = require('fs').promises;
const path = require('path');

class TestRunner {
  constructor() {
    this.results = [];
    this.screenshotDir = path.join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct');
  }

  async setup() {
    console.log('🚀 Setting up test environment...\n');
    
    try {
      await fs.mkdir(this.screenshotDir, { recursive: true });
      console.log(`✓ Screenshot directory created: ${this.screenshotDir}\n`);
    } catch (error) {
      console.error('Failed to create screenshot directory:', error.message);
    }
    
    console.log('🌐 Launching browser...');
    const { webkit } = require('playwright');
    this.browser = await webkit.launch({
      headless: false
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    this.page = await this.context.newPage();
    
    this.browserHelper = new BrowserHelper(this.page);
    this.authHelper = new AuthHelper(this.page, this.browserHelper);
    this.visualDebugger = new VisualDebugger(this.browserHelper);
    
    console.log('✓ Browser launched successfully\n');
  }

  async runDesktopTests() {
    console.log('💻 Running Desktop Tests...\n');
    console.log('=' .repeat(60));
    
    const tests = [
      { name: 'Authentication', fn: () => this.testAuthentication() },
      { name: 'Survey Management', fn: () => this.testSurveyManagement() },
      { name: 'Data Analysis', fn: () => this.testDataAnalysis() }
    ];
    
    for (const test of tests) {
      console.log(`\n📋 Test Suite: ${test.name}`);
      console.log('-'.repeat(60));
      
      try {
        await test.fn();
        this.results.push({ name: test.name, status: 'passed', error: null });
        console.log(`✅ ${test.name} - PASSED\n`);
      } catch (error) {
        this.results.push({ name: test.name, status: 'failed', error: error.message });
        console.error(`❌ ${test.name} - FAILED:`, error.message, '\n');
      }
    }
  }

  async runMobileTests() {
    console.log('\n📱 Running Mobile Tests...\n');
    console.log('=' .repeat(60));
    
    const mobileViewports = [
      { name: 'iPhone 12', width: 390, height: 844 },
      { name: 'Pixel 5', width: 393, height: 851 }
    ];
    
    for (const viewport of mobileViewports) {
      console.log(`\n📱 Testing on ${viewport.name} (${viewport.width}x${viewport.height})`);
      console.log('-'.repeat(60));
      
      await this.page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      try {
        await this.testMobileExperience(viewport.name);
        this.results.push({ name: `Mobile - ${viewport.name}`, status: 'passed', error: null });
        console.log(`✅ Mobile ${viewport.name} - PASSED\n`);
      } catch (error) {
        this.results.push({ name: `Mobile - ${viewport.name}`, status: 'failed', error: error.message });
        console.error(`❌ Mobile ${viewport.name} - FAILED:`, error.message, '\n');
      }
    }
    
    await this.page.setViewportSize({ width: 1920, height: 1080 });
  }

  async testAuthentication() {
    await this.page.goto('http://localhost:3000/login');
    await this.browserHelper.waitForPageLoad();
    
    await this.visualDebugger.analyzePage('desktop-login');
    
    const loginSuccess = await this.authHelper.login();
    
    if (!loginSuccess) {
      throw new Error('Login failed');
    }
    
    await this.browserHelper.logPageState('After login');
  }

  async testSurveyManagement() {
    await this.page.goto('http://localhost:3000/surveys');
    await this.browserHelper.waitForPageLoad();
    
    await this.visualDebugger.analyzePage('survey-list');
    
    const createButton = await this.page.$('button:has-text("新建"), button:has-text("创建")');
    if (createButton) {
      await createButton.click();
      await this.browserHelper.waitForPageLoad();
      
      await this.browserHelper.captureAndSave('survey-create-form', 'Survey creation form');
    }
  }

  async testDataAnalysis() {
    await this.page.goto('http://localhost:3000/analysis');
    await this.browserHelper.waitForPageLoad();
    
    await this.visualDebugger.analyzePage('analysis-page');
    
    const charts = await this.page.$$('canvas, .chart');
    console.log(`   Found ${charts.length} chart elements`);
    
    await this.browserHelper.captureAndSave('analysis-charts', 'Analysis charts view');
  }

  async testMobileExperience(deviceName) {
    await this.page.goto('http://localhost:3000/login');
    await this.browserHelper.waitForPageLoad();
    
    await this.browserHelper.captureAndSave(`mobile-${deviceName.toLowerCase().replace(' ', '-')}-login`, `Mobile login on ${deviceName}`);
    
    const layoutInfo = await this.visualDebugger.checkLayout(
      this.page.viewportSize(),
      `mobile-${deviceName.toLowerCase().replace(' ', '-')}`
    );
    
    if (layoutInfo.hasHorizontalScroll) {
      console.log('   ⚠️  Warning: Horizontal scroll detected');
    }
    
    const loginSuccess = await this.authHelper.login();
    
    if (!loginSuccess) {
      throw new Error('Mobile login failed');
    }
    
    await this.browserHelper.captureAndSave(`mobile-${deviceName.toLowerCase().replace(' ', '-')}-success`, `Mobile logged in on ${deviceName}`);
  }

  async generateReport() {
    console.log('\n📊 Generating Test Report...\n');
    console.log('=' .repeat(60));
    
    const report = {
      generatedAt: new Date().toISOString(),
      summary: {
        total: this.results.length,
        passed: this.results.filter(r => r.status === 'passed').length,
        failed: this.results.filter(r => r.status === 'failed').length
      },
      results: this.results
    };
    
    const reportPath = path.join(this.screenshotDir, 'test-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`Total Tests: ${report.summary.total}`);
    console.log(`Passed: ${report.summary.passed} ✅`);
    console.log(`Failed: ${report.summary.failed} ❌`);
    console.log(`\n📄 Report saved to: ${reportPath}`);
    console.log(`📸 Screenshots saved to: ${this.screenshotDir}`);
    
    return report;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
      console.log('\n✓ Browser closed');
    }
  }

  async run() {
    try {
      await this.setup();
      
      await this.runDesktopTests();
      
      await this.runMobileTests();
      
      const report = await this.generateReport();
      
      await this.cleanup();
      
      console.log('\n' + '='.repeat(60));
      console.log('✅ All tests completed!');
      console.log('='.repeat(60) + '\n');
      
      return report;
    } catch (error) {
      console.error('\n❌ Test execution failed:', error.message);
      await this.cleanup();
      throw error;
    }
  }
}

async function main() {
  const runner = new TestRunner();
  
  try {
    await runner.run();
    process.exit(0);
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = TestRunner;
