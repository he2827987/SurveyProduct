const fs = require('fs').promises;
const path = require('path');

class AuthHelper {
  constructor(page, browserHelper) {
    this.page = page;
    this.browserHelper = browserHelper;
    this.credentials = {
      email: 'he2827987@gmail.com',
      password: '13245678'
    };
    this.authFile = path.join(process.cwd(), 'auth-state.json');
  }

  async login() {
    console.log('🔐 Starting login process...');
    
    await this.browserHelper.waitForPageLoad();
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('before-login', 'Login page before authentication');
    
    const emailSelectors = [
      '.el-input input[placeholder*="邮箱"]',
      'input[placeholder*="邮箱"]',
      'input[placeholder*="email"]',
      'input[type="email"]',
      '.el-form-item:nth-child(1) input',
      '.login-form input.el-input__inner'
    ];
    
    const passwordSelectors = [
      '.el-input input[type="password"]',
      'input[type="password"]',
      'input[placeholder*="密码"]',
      '.el-form-item:nth-child(2) input[type="password"]',
      '.login-form input[type="password"]'
    ];
    
    let emailInput = null;
    let passwordInput = null;
    
    console.log('   🔍 Searching for email input...');
    for (const selector of emailSelectors) {
      try {
        await this.page.waitForSelector(selector, { state: 'visible', timeout: 2000 });
        emailInput = await this.page.$(selector);
        if (emailInput) {
          console.log(`   ✓ Found email input with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    console.log('   🔍 Searching for password input...');
    for (const selector of passwordSelectors) {
      try {
        await this.page.waitForSelector(selector, { state: 'visible', timeout: 2000 });
        passwordInput = await this.page.$(selector);
        if (passwordInput) {
          console.log(`   ✓ Found password input with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!emailInput || !passwordInput) {
      const pageInfo = await this.browserHelper.getPageInfo();
      console.log('   ⚠ Available inputs:', JSON.stringify(pageInfo.inputs, null, 2));
      console.log('   ⚠ Page HTML snippet:', await this.page.evaluate(() => document.body.innerHTML.substring(0, 500)));
      throw new Error('Login form not found - email or password input missing');
    }
    
    await emailInput.click();
    await emailInput.fill('');
    await emailInput.type(this.credentials.email, { delay: 50 });
    console.log(`   ✓ Email filled: ${this.credentials.email}`);
    
    await passwordInput.click();
    await passwordInput.fill('');
    await passwordInput.type(this.credentials.password, { delay: 50 });
    console.log('   ✓ Password filled');
    
    await this.browserHelper.captureAndSave('login-form-filled', 'Login form with credentials');
    
    const buttonSelectors = [
      'button.el-button--primary:has-text("登录")',
      'button:has-text("登录")',
      'button[type="primary"]:has-text("登录")',
      '.login-form button.el-button--primary',
      'button.el-button:has-text("登录")'
    ];
    
    let loginButton = null;
    console.log('   🔍 Searching for login button...');
    for (const selector of buttonSelectors) {
      try {
        await this.page.waitForSelector(selector, { state: 'visible', timeout: 2000 });
        loginButton = await this.page.$(selector);
        if (loginButton) {
          console.log(`   ✓ Found login button with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!loginButton) {
      throw new Error('Login button not found');
    }
    
    await loginButton.click();
    console.log('   ✓ Login button clicked');
    
    await this.page.waitForTimeout(3000);
    
    await this.browserHelper.captureAndSave('after-login-click', 'Page after clicking login');
    
    try {
      await this.page.waitForURL(url => !url.includes('/login'), { timeout: 10000 });
      console.log('   ✓ Redirected from login page');
    } catch (error) {
      console.log('   ⚠ Still on login page or redirect timeout');
    }
    
    await this.browserHelper.waitForPageLoad();
    
    const currentUrl = this.page.url();
    const isLoggedIn = !currentUrl.includes('/login');
    
    if (isLoggedIn) {
      console.log(`   ✅ Login successful - Current URL: ${currentUrl}`);
      await this.browserHelper.captureAndSave('login-success', 'Successfully logged in');
    } else {
      console.log(`   ❌ Login failed - Still on: ${currentUrl}`);
      await this.browserHelper.captureAndSave('login-failed', 'Login attempt failed');
    }
    
    return isLoggedIn;
  }

  async logout() {
    console.log('🔓 Starting logout process...');
    
    await this.browserHelper.captureAndSave('before-logout', 'Page before logout');
    
    const userMenu = await this.page.$('[class*="user-menu"], [class*="avatar"], button:has-text("退出"), button:has-text("登出")');
    
    if (userMenu) {
      await userMenu.click();
      await this.page.waitForTimeout(500);
      
      const logoutButton = await this.page.$('button:has-text("退出"), button:has-text("登出"), a:has-text("退出"), a:has-text("登出")');
      
      if (logoutButton) {
        await logoutButton.click();
        await this.browserHelper.waitForPageLoad();
        console.log('   ✓ Logout successful');
      }
    }
    
    await this.browserHelper.captureAndSave('after-logout', 'Page after logout');
  }

  async saveAuthState(context) {
    try {
      await context.storageState({ path: this.authFile });
      console.log(`   ✓ Auth state saved to ${this.authFile}`);
    } catch (error) {
      console.error('   ✗ Failed to save auth state:', error.message);
    }
  }

  async loadAuthState() {
    try {
      const state = await fs.readFile(this.authFile, 'utf-8');
      console.log('   ✓ Auth state loaded');
      return JSON.parse(state);
    } catch (error) {
      console.log('   ⚠ No saved auth state found');
      return null;
    }
  }

  async isAuthenticated() {
    const currentUrl = this.page.url();
    if (currentUrl.includes('/login')) {
      return false;
    }
    
    const token = await this.page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token') || sessionStorage.getItem('token');
    });
    
    return !!token;
  }

  async ensureAuthenticated() {
    const isAuth = await this.isAuthenticated();
    
    if (!isAuth) {
      console.log('   ⚠ Not authenticated, performing login...');
      await this.page.goto('/login');
      await this.browserHelper.waitForPageLoad();
      return await this.login();
    }
    
    console.log('   ✓ Already authenticated');
    return true;
  }

  async checkAuthStatus() {
    const info = await this.browserHelper.getPageInfo();
    const isAuth = await this.isAuthenticated();
    
    console.log('\n=== Auth Status ===');
    console.log(`Authenticated: ${isAuth}`);
    console.log(`Current URL: ${info.url}`);
    console.log(`Page Title: ${info.title}`);
    console.log('==================\n');
    
    return {
      isAuthenticated: isAuth,
      url: info.url,
      title: info.title
    };
  }
}

module.exports = { AuthHelper };
