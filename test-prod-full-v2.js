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

async function login(page) {
  await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.locator('input[placeholder*="邮箱"]').fill(TEST_EMAIL);
  await page.locator('input[type="password"]').fill(TEST_PASSWORD);
  await page.locator('button:has-text("登录")').click();
  await page.waitForURL('**/dashboard**', { timeout: 15000 });
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
}

async function clickSidebarMenu(page, menuText) {
  const menuItem = page.locator(`.el-menu-vertical .el-menu-item`).filter({ hasText: menuText }).first();
  await menuItem.click({ timeout: 5000 });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    locale: 'zh-CN',
  });
  const page = await context.newPage();

  page.on('pageerror', err => console.log(`  ⚠️ Page Error: ${err.message}`));

  console.log('\n========================================');
  console.log('   PRODUCTION FRONTEND TEST SUITE v2');
  console.log('========================================\n');

  // ===== TEST 1: Login Page =====
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

    const switchLink = page.locator('text=立即注册');
    const switchCount = await switchLink.count();
    if (switchCount > 0) {
      logPass('Register switch link present');
    } else {
      logFail('Register switch link present', 'Not found');
    }
  } catch (e) {
    logFail('Login page', e.message);
  }

  // ===== TEST 2: Register Form Switch =====
  console.log('\n--- Test 2: Register Form Switch ---');
  try {
    await page.locator('text=立即注册').first().click();
    await page.waitForTimeout(1000);

    const usernameInput = page.locator('input[placeholder*="用户名"]');
    const confirmInput = page.locator('input[placeholder*="确认"]');
    const uCount = await usernameInput.count();
    const cCount = await confirmInput.count();
    if (uCount > 0 && cCount > 0) {
      logPass('Register form shows username and confirm password');
    } else {
      logFail('Register form shows username and confirm password', `Username: ${uCount}, Confirm: ${cCount}`);
    }

    const registerBtn = page.locator('button:has-text("注册")');
    const rCount = await registerBtn.count();
    if (rCount > 0) {
      logPass('Register button present');
    } else {
      logFail('Register button present', 'Not found');
    }

    // Switch back to login
    await page.locator('text=返回登录').first().click();
    await page.waitForTimeout(500);
    const loginBtnCount = await page.locator('button:has-text("登录")').count();
    if (loginBtnCount > 0) {
      logPass('Switch back to login mode works');
    } else {
      logFail('Switch back to login mode works', 'Login button not found after switching back');
    }

    await page.screenshot({ path: 'test-v2-02-register.png' });
  } catch (e) {
    logFail('Register form switch', e.message);
  }

  // ===== TEST 3: Login Flow =====
  console.log('\n--- Test 3: Login Flow ---');
  try {
    await page.locator('input[placeholder*="邮箱"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.locator('button:has-text("登录")').click();

    const navigated = await page.waitForURL('**/dashboard**', { timeout: 15000 });
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

    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  } catch (e) {
    logFail('Login flow', e.message);
  }

  // ===== TEST 4: Dashboard =====
  console.log('\n--- Test 4: Dashboard Page ---');
  try {
    await page.screenshot({ path: 'test-v2-04-dashboard.png' });
    const pageContent = await page.textContent('body').catch(() => '');
    if (pageContent.includes('仪表板') || pageContent.includes('首页') || pageContent.includes('统计') || pageContent.includes('调研')) {
      logPass('Dashboard page has content');
    } else {
      logFail('Dashboard page has content', `Preview: ${pageContent.substring(0, 200)}`);
    }

    const hasLayout = await page.locator('.layout-container, .el-menu, .el-aside').count();
    if (hasLayout > 0) {
      logPass('Layout with sidebar present');
    } else {
      logFail('Layout with sidebar present', 'Layout elements not found');
    }

    const hasSidebar = await page.locator('.el-menu-vertical').count();
    if (hasSidebar > 0) {
      logPass('Sidebar menu present');
    } else {
      logFail('Sidebar menu present', 'Not found');
    }
  } catch (e) {
    logFail('Dashboard page', e.message);
  }

  // ===== TEST 5: Navigate to Survey Management =====
  console.log('\n--- Test 5: Survey Management Page ---');
  try {
    await clickSidebarMenu(page, '调研管理');
    await page.waitForURL('**/survey**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-05-survey.png' });

    if (page.url().includes('/survey')) {
      logPass('Navigated to survey page');
    } else {
      logFail('Navigated to survey page', `URL: ${page.url()}`);
    }

    const pageContent = await page.textContent('body').catch(() => '');
    const hasContent = pageContent.includes('调研') || pageContent.includes('创建') || pageContent.includes('列表');
    if (hasContent) {
      logPass('Survey page has relevant content');
    } else {
      logFail('Survey page has relevant content', `Preview: ${pageContent.substring(0, 300)}`);
    }
  } catch (e) {
    logFail('Survey management', e.message);
  }

  // ===== TEST 6: Question Bank =====
  console.log('\n--- Test 6: Question Bank Page ---');
  try {
    await clickSidebarMenu(page, '题库管理');
    await page.waitForURL('**/question**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-06-question.png' });

    if (page.url().includes('/question')) {
      logPass('Navigated to question bank page');
    } else {
      logFail('Navigated to question bank page', `URL: ${page.url()}`);
    }

    const pageContent = await page.textContent('body').catch(() => '');
    if (pageContent.includes('题库') || pageContent.includes('问题') || pageContent.includes('题目')) {
      logPass('Question bank page has relevant content');
    } else {
      logFail('Question bank page has relevant content', `Preview: ${pageContent.substring(0, 300)}`);
    }
  } catch (e) {
    logFail('Question bank', e.message);
  }

  // ===== TEST 7: Organization =====
  console.log('\n--- Test 7: Organization Page ---');
  try {
    await clickSidebarMenu(page, '组织架构管理');
    await page.waitForURL('**/organization**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-07-org.png' });

    if (page.url().includes('/organization')) {
      logPass('Navigated to organization page');
    } else {
      logFail('Navigated to organization page', `URL: ${page.url()}`);
    }
  } catch (e) {
    logFail('Organization page', e.message);
  }

  // ===== TEST 8: Analysis =====
  console.log('\n--- Test 8: Data Analysis Page ---');
  try {
    await clickSidebarMenu(page, '数据分析');
    await page.waitForURL('**/analysis**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-08-analysis.png' });

    if (page.url().includes('/analysis')) {
      logPass('Navigated to analysis page');
    } else {
      logFail('Navigated to analysis page', `URL: ${page.url()}`);
    }
  } catch (e) {
    logFail('Analysis page', e.message);
  }

  // ===== TEST 9: Compare =====
  console.log('\n--- Test 9: Enterprise Compare Page ---');
  try {
    await clickSidebarMenu(page, '企业对比');
    await page.waitForURL('**/compare**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-09-compare.png' });

    if (page.url().includes('/compare')) {
      logPass('Navigated to compare page');
    } else {
      logFail('Navigated to compare page', `URL: ${page.url()}`);
    }
  } catch (e) {
    logFail('Compare page', e.message);
  }

  // ===== TEST 10: Profile via Dropdown =====
  console.log('\n--- Test 10: Profile Page (via dropdown) ---');
  try {
    // Click the user dropdown trigger
    const userDropdown = page.locator('.user-dropdown').first();
    await userDropdown.click({ timeout: 5000 });
    await page.waitForTimeout(500);

    // Click "个人信息" dropdown item
    const profileItem = page.locator('.el-dropdown-menu__item').filter({ hasText: '个人信息' }).first();
    await profileItem.click({ timeout: 5000 });
    await page.waitForURL('**/profile**', { timeout: 10000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: 'test-v2-10-profile.png' });

    if (page.url().includes('/profile')) {
      logPass('Navigated to profile page');
    } else {
      logFail('Navigated to profile page', `URL: ${page.url()}`);
    }

    const pageContent = await page.textContent('body').catch(() => '');
    if (pageContent.includes('个人信息') || pageContent.includes('密码') || pageContent.includes('用户')) {
      logPass('Profile page has relevant content');
    } else {
      logFail('Profile page has relevant content', `Preview: ${pageContent.substring(0, 300)}`);
    }
  } catch (e) {
    logFail('Profile page', e.message);
  }

  // ===== TEST 11: Logout via Dropdown =====
  console.log('\n--- Test 11: Logout (via dropdown) ---');
  try {
    // Navigate to a page first (in case we're on profile)
    await clickSidebarMenu(page, '首页');
    await page.waitForTimeout(1000);

    // Click user dropdown
    const userDropdown = page.locator('.user-dropdown').first();
    await userDropdown.click({ timeout: 5000 });
    await page.waitForTimeout(500);

    // Click "退出登录"
    const logoutItem = page.locator('.el-dropdown-menu__item').filter({ hasText: '退出登录' }).first();
    await logoutItem.click({ timeout: 5000 });

    // Handle confirmation dialog
    await page.waitForTimeout(1000);
    const confirmBtn = page.locator('.el-message-box__btns button').filter({ hasText: '确定' }).first();
    const confirmExists = await confirmBtn.count();
    if (confirmExists > 0) {
      await confirmBtn.click();
    }

    await page.waitForURL('**/login**', { timeout: 10000 });
    await page.screenshot({ path: 'test-v2-11-logout.png' });

    if (page.url().includes('/login')) {
      logPass('Logout redirects to login page');
    } else {
      logFail('Logout redirects to login page', `URL: ${page.url()}`);
    }

    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    if (!token) {
      logPass('Token cleared after logout');
    } else {
      logFail('Token cleared after logout', 'Token still exists');
    }
  } catch (e) {
    logFail('Logout', e.message);
  }

  // ===== TEST 12: Auth Guard =====
  console.log('\n--- Test 12: Auth Guard ---');
  try {
    await page.goto(`${PROD_URL}/dashboard`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    if (page.url().includes('/login')) {
      logPass('Unauthenticated access to /dashboard redirects to /login');
    } else {
      logFail('Unauthenticated access to /dashboard redirects to /login', `URL: ${page.url()}`);
    }
  } catch (e) {
    logFail('Auth guard', e.message);
  }

  // ===== TEST 13: SPA Refresh =====
  console.log('\n--- Test 13: SPA Refresh ---');
  try {
    // Login again
    await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.locator('input[placeholder*="邮箱"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    await page.waitForURL('**/dashboard**', { timeout: 15000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

    // Navigate to survey
    await clickSidebarMenu(page, '调研管理');
    await page.waitForURL('**/survey**', { timeout: 10000 });

    // Refresh
    await page.reload({ waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    if (page.url().includes('/survey')) {
      logPass('SPA refresh on /survey stays on /survey');
    } else if (page.url().includes('/login')) {
      logFail('SPA refresh on /survey stays on /survey', 'Redirected to login (token expired during test)');
    } else {
      logFail('SPA refresh on /survey stays on /survey', `URL: ${page.url()}`);
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

  const passRate = Math.round((results.passed.length / (results.passed.length + results.failed.length)) * 100);
  console.log(`\n  Pass rate: ${passRate}%`);
  console.log('\n========================================\n');

  await browser.close();
})();
