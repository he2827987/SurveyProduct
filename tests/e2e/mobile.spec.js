const { test, expect } = require('@playwright/test');
const { BrowserHelper } = require('../helpers/browser-helper');
const { AuthHelper } = require('../helpers/auth-helper');
const { VisualDebugger } = require('../helpers/visual-debug');

test.describe('Mobile Tests', () => {
  let browserHelper;
  let authHelper;
  let visualDebugger;

  test.beforeEach(async ({ page }) => {
    browserHelper = new BrowserHelper(page);
    authHelper = new AuthHelper(page, browserHelper);
    visualDebugger = new VisualDebugger(browserHelper);
  });

  test('should display mobile login page correctly', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Login Page Display');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    const layoutInfo = await visualDebugger.checkLayout(
      page.viewportSize(),
      'mobile-login'
    );
    
    expect(layoutInfo.hasHorizontalScroll).toBeFalsy();
    
    const emailInput = await page.$('input[type="email"], input[placeholder*="邮箱"]');
    expect(emailInput).toBeTruthy();
    
    await browserHelper.logPageState('Mobile login page');
  });

  test('should login successfully on mobile', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Login');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    const loginSuccess = await authHelper.login();
    expect(loginSuccess).toBeTruthy();
    
    await browserHelper.captureAndSave('mobile-login-success', 'Mobile login successful');
  });

  test('should navigate mobile menu', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Menu Navigation');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    await authHelper.login();
    
    const menuButton = await page.$('.hamburger, .menu-toggle, [class*="menu-button"], button[aria-label*="menu"]');
    
    if (menuButton) {
      await menuButton.click();
      await page.waitForTimeout(500);
      
      await browserHelper.captureAndSave('mobile-menu-open', 'Mobile menu opened');
      
      const menuItems = await page.$$('.menu-item, nav a, [class*="nav-item"]');
      if (menuItems.length > 0) {
        await menuItems[0].click();
        await browserHelper.waitForPageLoad();
        
        await browserHelper.captureAndSave('mobile-menu-navigated', 'Navigated via mobile menu');
      }
    } else {
      console.log('   ⚠ Mobile menu button not found');
    }
  });

  test('should fill survey on mobile', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Fill Survey');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    await authHelper.login();
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('mobile-survey-list', 'Mobile survey list');
    
    const surveyItems = await page.$$('.survey-item, .survey-card, [class*="survey"]');
    
    if (surveyItems.length > 0) {
      await surveyItems[0].click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('mobile-survey-detail', 'Mobile survey detail');
      
      const startButton = await page.$('button:has-text("开始"), button:has-text("填写"), button:has-text("Start")');
      if (startButton) {
        await startButton.click();
        await browserHelper.waitForPageLoad();
        
        await browserHelper.captureAndSave('mobile-survey-form', 'Mobile survey form');
        
        const inputs = await page.$$('input:visible, textarea:visible, select:visible');
        console.log(`   Found ${inputs.length} visible input fields`);
        
        for (let i = 0; i < Math.min(3, inputs.length); i++) {
          const input = inputs[i];
          const type = await input.getAttribute('type');
          
          if (type === 'text' || type === 'textarea') {
            await input.fill('测试答案 ' + (i + 1));
          } else if (type === 'radio' || type === 'checkbox') {
            await input.click();
          }
          
          await page.waitForTimeout(300);
        }
        
        await browserHelper.captureAndSave('mobile-survey-filled', 'Mobile survey partially filled');
      }
    } else {
      console.log('   ⚠ No surveys found');
    }
  });

  test('should handle mobile scrolling', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Scroll Behavior');
    
    await page.goto('/');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('mobile-top', 'Mobile page top');
    
    await browserHelper.scrollDown(300);
    await browserHelper.captureAndSave('mobile-scrolled-down', 'Mobile scrolled down');
    
    await browserHelper.scrollToBottom();
    await browserHelper.captureAndSave('mobile-bottom', 'Mobile page bottom');
    
    await browserHelper.scrollToTop();
    await browserHelper.captureAndSave('mobile-back-to-top', 'Mobile back to top');
  });

  test('should handle touch interactions', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Touch Interactions');
    
    await page.goto('/');
    await browserHelper.waitForPageLoad();
    
    const touchArea = await page.$('body');
    if (touchArea) {
      const box = await touchArea.boundingBox();
      if (box) {
        await page.touchscreen.tap(box.x + box.width / 2, box.y + 100);
        await page.waitForTimeout(500);
        
        await browserHelper.captureAndSave('mobile-tap', 'After touch tap');
      }
    }
  });

  test('should display responsive charts on mobile', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Responsive Charts');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    await authHelper.login();
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('mobile-charts', 'Mobile analysis charts');
    
    const charts = await page.$$('canvas, .chart, [class*="echarts"]');
    console.log(`   ✓ Found ${charts.length} chart elements on mobile`);
    
    for (let i = 0; i < charts.length; i++) {
      const chart = charts[i];
      const isVisible = await chart.isVisible();
      const box = await chart.boundingBox();
      
      if (box) {
        console.log(`   Chart ${i + 1}: ${box.width}x${box.height}, visible: ${isVisible}`);
      }
    }
  });

  test('should handle mobile keyboard', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Mobile Keyboard');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    const emailInput = await page.$('input[type="email"], input[placeholder*="邮箱"]');
    if (emailInput) {
      await emailInput.tap();
      await page.waitForTimeout(500);
      
      await browserHelper.captureAndSave('mobile-keyboard-open', 'Mobile keyboard opened');
      
      await emailInput.fill('test@example.com');
      await page.waitForTimeout(300);
      
      await browserHelper.captureAndSave('mobile-typed', 'Text typed on mobile');
    }
  });

  test('should adapt layout on orientation change', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Orientation Change');
    
    await page.goto('/');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('mobile-portrait', 'Portrait orientation');
    
    const landscape = { width: 812, height: 375 };
    await page.setViewportSize(landscape);
    await page.waitForTimeout(500);
    
    await browserHelper.captureAndSave('mobile-landscape', 'Landscape orientation');
    
    const portrait = { width: 375, height: 812 };
    await page.setViewportSize(portrait);
    await page.waitForTimeout(500);
    
    await browserHelper.captureAndSave('mobile-portrait-again', 'Back to portrait');
  });

  test('should handle mobile form submission', async ({ page }) => {
    console.log('\n🧪 Mobile Test: Form Submission');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    await authHelper.login();
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    const createButton = await page.$('button:has-text("新建"), button:has-text("创建")');
    if (createButton) {
      await createButton.click();
      await browserHelper.waitForPageLoad();
      
      const titleInput = await page.$('input[placeholder*="标题"], input[name="title"]');
      if (titleInput) {
        await titleInput.tap();
        await titleInput.fill('移动端测试问卷');
        
        await browserHelper.captureAndSave('mobile-form-filled', 'Mobile form filled');
        
        const submitButton = await page.$('button:has-text("提交"), button[type="submit"]');
        if (submitButton) {
          await submitButton.tap();
          await browserHelper.waitForPageLoad();
          
          await browserHelper.captureAndSave('mobile-form-submitted', 'Mobile form submitted');
        }
      }
    }
  });
});
