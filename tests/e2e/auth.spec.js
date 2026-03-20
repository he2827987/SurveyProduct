const { test, expect } = require('@playwright/test');
const { BrowserHelper } = require('../helpers/browser-helper');
const { AuthHelper } = require('../helpers/auth-helper');
const { VisualDebugger } = require('../helpers/visual-debug');

test.describe('Authentication Tests', () => {
  let browserHelper;
  let authHelper;
  let visualDebugger;

  test.beforeEach(async ({ page }) => {
    browserHelper = new BrowserHelper(page);
    authHelper = new AuthHelper(page, browserHelper);
    visualDebugger = new VisualDebugger(browserHelper);
  });

  test('should display login page correctly', async ({ page }) => {
    console.log('\n🧪 Test: Login Page Display');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    await visualDebugger.analyzePage('login-page');
    
    const emailInput = await page.$('input[type="email"], input[placeholder*="邮箱"], input[placeholder*="email"]');
    expect(emailInput).toBeTruthy();
    
    const passwordInput = await page.$('input[type="password"], input[placeholder*="密码"], input[placeholder*="password"]');
    expect(passwordInput).toBeTruthy();
    
    const loginButton = await page.$('button:has-text("登录"), button:has-text("Login"), button[type="submit"]');
    expect(loginButton).toBeTruthy();
    
    await browserHelper.logPageState('Login page loaded');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    console.log('\n🧪 Test: Successful Login');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    const loginSuccess = await authHelper.login();
    expect(loginSuccess).toBeTruthy();
    
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('/login');
    
    await browserHelper.logPageState('After successful login');
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    console.log('\n🧪 Test: Failed Login with Invalid Credentials');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    const emailInput = await page.$('input[type="email"], input[placeholder*="邮箱"], input[placeholder*="email"]');
    await emailInput.fill('invalid@example.com');
    
    const passwordInput = await page.$('input[type="password"], input[placeholder*="密码"], input[placeholder*="password"]');
    await passwordInput.fill('wrongpassword');
    
    await browserHelper.captureAndSave('invalid-credentials-filled', 'Form filled with invalid credentials');
    
    const loginButton = await page.$('button:has-text("登录"), button:has-text("Login"), button[type="submit"]');
    await loginButton.click();
    
    await page.waitForTimeout(2000);
    
    await browserHelper.captureAndSave('invalid-login-result', 'After invalid login attempt');
    
    const pageInfo = await browserHelper.getPageInfo();
    const hasError = pageInfo.alerts.length > 0 || page.url().includes('/login');
    
    expect(hasError).toBeTruthy();
  });

  test('should logout successfully', async ({ page }) => {
    console.log('\n🧪 Test: Logout');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    await authHelper.login();
    
    await authHelper.logout();
    
    await browserHelper.logPageState('After logout');
  });

  test('should maintain authentication state', async ({ page, context }) => {
    console.log('\n🧪 Test: Authentication State Persistence');
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    
    await authHelper.login();
    
    await authHelper.saveAuthState(context);
    
    await page.goto('/dashboard');
    await browserHelper.waitForPageLoad();
    
    const isAuth = await authHelper.isAuthenticated();
    expect(isAuth).toBeTruthy();
    
    await browserHelper.logPageState('Authentication state verified');
  });
});
