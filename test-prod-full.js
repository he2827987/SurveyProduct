const { chromium } = require('playwright');

const PROD_URL = 'https://surveyproduct.onrender.com';
const TEST_EMAIL = 'testuser_prod@test.com';
const TEST_PASSWORD = 'Test123456';

const results = { passed: [], failed: [] };

function logPass(name) {
  results.passed.push(name);
  console.log(`  ✅ PASS: ${name}`);
}

function logFail(name, detail) {
  results.failed.push({ name, detail });
  console.log(`  ❌ FAIL: ${name} — ${detail}`);
}

async function safeClick(page, selector, timeout = 5000) {
  try {
    await page.locator(selector).first().click({ timeout });
    return true;
  } catch {
    return false;
  }
}

async function safeFill(page, selector, value, timeout = 5000) {
  try {
    await page.locator(selector).first().fill(value, { timeout });
    return true;
  } catch {
    return false;
  }
}

async function waitForUrl(page, path, timeout = 10000) {
  try {
    await page.waitForURL(`**${path}**`, { timeout });
    return true;
  } catch {
    return false;
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    locale: 'zh-CN',
  });
  const page = await context.newPage();

  page.on('pageerror', err => {
    console.log(`  ⚠️ Page Error: ${err.message}`);
  });

  console.log('\n========================================');
  console.log('   PRODUCTION FRONTEND TEST SUITE');
  console.log('========================================\n');

  // ===== TEST 1: Login Page Loads =====
  console.log('--- Test 1: Login Page ---');
  try {
    await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 60000 });
    const h2 = await page.textContent('h2').catch(() => null);
    if (h2 && h2.includes('企业问卷调查系统')) {
      logPass('Login page renders with correct title');
    } else {
      logFail('Login page renders with correct title', `Got: ${h2}`);
    }

    const inputs = await page.locator('input').count();
    if (inputs >= 2) {
      logPass('Login form has email and password inputs');
    } else {
      logFail('Login form has email and password inputs', `Found ${inputs} inputs`);
    }

    const loginBtn = await page.locator('button:has-text("登录")').count();
    if (loginBtn > 0) {
      logPass('Login button present');
    } else {
      logFail('Login button present', 'Not found');
    }
  } catch (e) {
    logFail('Login page loads', e.message);
  }

  // ===== TEST 2: Login Works =====
  console.log('\n--- Test 2: Login Flow ---');
  try {
    await page.locator('input[placeholder*="邮箱"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.locator('button:has-text("登录")').click();

    const navigated = await waitForUrl(page, '/dashboard', 15000);
    if (navigated) {
      logPass('Login redirects to /dashboard');
    } else {
      logFail('Login redirects to /dashboard', `Current URL: ${page.url()}`);
    }

    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    if (token) {
      logPass('Token saved to localStorage');
    } else {
      logFail('Token saved to localStorage', 'No token found');
    }
  } catch (e) {
    logFail('Login flow', e.message);
  }

  // ===== TEST 3: Dashboard Page =====
  console.log('\n--- Test 3: Dashboard Page ---');
  try {
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => { });
    await page.screenshot({ path: 'test-03-dashboard.png' });

    const pageContent = await page.textContent('body').catch(() => '');
    if (pageContent.includes('仪表板') || pageContent.includes('dashboard') || pageContent.includes('调研') || pageContent.includes('统计')) {
      logPass('Dashboard page has content');
    } else {
      logFail('Dashboard page has content', `Content preview: ${pageContent.substring(0, 200)}`);
    }

    const hasLayout = await page.locator('.layout-container, .el-menu, .el-aside, .sidebar').count();
    if (hasLayout > 0) {
      logPass('Layout navigation sidebar present');
    } else {
      logFail('Layout navigation sidebar present', `Layout elements: ${hasLayout}`);
    }
  } catch (e) {
    logFail('Dashboard page', e.message);
  }

  // ===== TEST 4: Navigation - Survey Management =====
  console.log('\n--- Test 4: Survey Management Page ---');
  try {
    const surveyLink = page.locator('text=调研管理').first();
    await surveyLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('调研') || text.includes('survey'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-04-survey.png' });

    const url = page.url();
    if (url.includes('/survey')) {
      logPass('Navigated to survey page');
    } else {
      logFail('Navigated to survey page', `URL: ${url}`);
    }

    const pageContent = await page.textContent('body').catch(() => '');
    const hasSurveyContent = pageContent.includes('调研') || pageContent.includes('创建') || pageContent.includes('列表') || pageContent.includes('问卷') || pageContent.includes('Survey');
    if (hasSurveyContent) {
      logPass('Survey page has relevant content');
    } else {
      logFail('Survey page has relevant content', `Preview: ${pageContent.substring(0, 300)}`);
    }
  } catch (e) {
    logFail('Survey management page', e.message);
  }

  // ===== TEST 5: Question Bank =====
  console.log('\n--- Test 5: Question Bank Page ---');
  try {
    const questionLink = page.locator('text=题库').first();
    await questionLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('题库') || text.includes('question'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-05-question.png' });

    const url = page.url();
    if (url.includes('/question')) {
      logPass('Navigated to question bank page');
    } else {
      logFail('Navigated to question bank page', `URL: ${url}`);
    }
  } catch (e) {
    logFail('Question bank page', e.message);
  }

  // ===== TEST 6: Organization Page =====
  console.log('\n--- Test 6: Organization Page ---');
  try {
    const orgLink = page.locator('text=组织').first();
    await orgLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('组织') || text.includes('org'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-06-org.png' });

    const url = page.url();
    if (url.includes('/organization')) {
      logPass('Navigated to organization page');
    } else {
      logFail('Navigated to organization page', `URL: ${url}`);
    }
  } catch (e) {
    logFail('Organization page', e.message);
  }

  // ===== TEST 7: Analysis Page =====
  console.log('\n--- Test 7: Analysis Page ---');
  try {
    const analysisLink = page.locator('text=数据分析').first();
    await analysisLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('分析') || text.includes('analysis') || text.includes('数据'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-07-analysis.png' });

    const url = page.url();
    if (url.includes('/analysis')) {
      logPass('Navigated to analysis page');
    } else {
      logFail('Navigated to analysis page', `URL: ${url}`);
    }
  } catch (e) {
    logFail('Analysis page', e.message);
  }

  // ===== TEST 8: Compare Page =====
  console.log('\n--- Test 8: Compare Page ---');
  try {
    const compareLink = page.locator('text=企业对比').first();
    await compareLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('对比') || text.includes('compare'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-08-compare.png' });

    const url = page.url();
    if (url.includes('/compare')) {
      logPass('Navigated to compare page');
    } else {
      logFail('Navigated to compare page', `URL: ${url}`);
    }
  } catch (e) {
    logFail('Compare page', e.message);
  }

  // ===== TEST 9: Profile Page =====
  console.log('\n--- Test 9: Profile Page ---');
  try {
    const profileLink = page.locator('text=个人信息').first();
    await profileLink.click({ timeout: 5000 }).catch(async () => {
      const menuItems = page.locator('.el-menu-item, .el-sub-menu__title, [role="menuitem"]');
      const count = await menuItems.count();
      for (let i = 0; i < count; i++) {
        const text = await menuItems.nth(i).textContent();
        if (text && (text.includes('个人信息') || text.includes('profile'))) {
          await menuItems.nth(i).click();
          break;
        }
      }
    });

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-09-profile.png' });

    const url = page.url();
    if (url.includes('/profile')) {
      logPass('Navigated to profile page');
    } else {
      logFail('Navigated to profile page', `URL: ${url}`);
    }
  } catch (e) {
    logFail('Profile page', e.message);
  }

  // ===== TEST 10: Logout =====
  console.log('\n--- Test 10: Logout ---');
  try {
    const logoutBtn = page.locator('text=退出').first();
    const logoutExists = await logoutBtn.count();
    if (logoutExists > 0) {
      await logoutBtn.click().catch(() => { });
      await page.waitForTimeout(2000);
      const url = page.url();
      if (url.includes('/login')) {
        logPass('Logout redirects to login');
      } else {
        logFail('Logout redirects to login', `URL: ${url}`);
      }
    } else {
      const token2 = await page.evaluate(() => localStorage.getItem('access_token'));
      await page.evaluate(() => localStorage.clear());
      await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
      const url = page.url();
      if (url.includes('/login')) {
        logPass('Manual logout (clear token) redirects to login');
      } else {
        logFail('Manual logout (clear token) redirects to login', `URL: ${url}`);
      }
    }
  } catch (e) {
    logFail('Logout', e.message);
  }

  // ===== TEST 11: Register Form Switch =====
  console.log('\n--- Test 11: Register Form ---');
  try {
    await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    const switchLink = page.locator('text=立即注册').first();
    const switchExists = await switchLink.count();
    if (switchExists > 0) {
      await switchLink.click();
      await page.waitForTimeout(1000);

      const usernameInput = page.locator('input[placeholder*="用户名"]');
      const confirmInput = page.locator('input[placeholder*="确认"]');
      const uCount = await usernameInput.count();
      const cCount = await confirmInput.count();
      if (uCount > 0 && cCount > 0) {
        logPass('Register form shows username and confirm password');
      } else {
        logFail('Register form shows username and confirm password', `Username inputs: ${uCount}, Confirm inputs: ${cCount}`);
      }

      const registerBtn = page.locator('button:has-text("注册")');
      const rCount = await registerBtn.count();
      if (rCount > 0) {
        logPass('Register button present');
      } else {
        logFail('Register button present', 'Not found');
      }

      await page.screenshot({ path: 'test-11-register.png' });
    } else {
      logFail('Register form switch link', '立即注册 link not found');
    }
  } catch (e) {
    logFail('Register form', e.message);
  }

  // ===== TEST 12: SPA Refresh =====
  console.log('\n--- Test 12: SPA Refresh (no 404) ---');
  try {
    await page.evaluate(() => localStorage.clear());
    await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.locator('input[placeholder*="邮箱"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    await waitForUrl(page, '/dashboard', 15000);

    await page.reload({ waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    const urlAfterRefresh = page.url();
    if (urlAfterRefresh.includes('/dashboard')) {
      logPass('SPA refresh on /dashboard stays on /dashboard');
    } else if (urlAfterRefresh.includes('/login')) {
      logFail('SPA refresh on /dashboard stays on /dashboard', 'Redirected to login (token may have expired)');
    } else {
      logFail('SPA refresh on /dashboard stays on /dashboard', `URL: ${urlAfterRefresh}`);
    }
  } catch (e) {
    logFail('SPA refresh', e.message);
  }

  // ===== SUMMARY =====
  console.log('\n========================================');
  console.log('   TEST SUMMARY');
  console.log('========================================');
  console.log(`  Passed: ${results.passed.length}`);
  console.log(`  Failed: ${results.failed.length}`);
  console.log(`  Total:  ${results.passed.length + results.failed.length}`);

  if (results.failed.length > 0) {
    console.log('\n  Failed tests:');
    results.failed.forEach(f => {
      console.log(`    ❌ ${f.name}: ${f.detail}`);
    });
  }

  console.log('\n========================================\n');

  await browser.close();
})();
