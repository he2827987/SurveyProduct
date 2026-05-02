const { chromium } = require('playwright');
const PROD = 'https://surveyproduct.onrender.com';
const SCREENSHOT_DIR = require('path').join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct', 'prod-test');
const fs = require('fs');

let issues = [];
let step = 0;
let token = '';

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function screenshot(page, name) {
  step++;
  if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const path = `${SCREENSHOT_DIR}/${String(step).padStart(2,'0')}_${name}.png`;
  await page.screenshot({ path, fullPage: true });
  console.log(`  [${step}] Screenshot: ${name}`);
}
function reportIssue(page, area, description) {
  issues.push({ area, description, url: page.url() });
  console.log(`  !! ISSUE: [${area}] ${description}`);
}

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  console.log(`\n=== Production Frontend Test ===`);
  console.log(`URL: ${PROD}\n`);

  // ===== 1. Load Home/Login Page =====
  console.log('--- 1. Login Page ---');
  await page.goto(`${PROD}/login`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await screenshot(page, 'login-page');

  const bodyText = await page.textContent('body').catch(() => '');
  if (bodyText.includes('登录') || bodyText.includes('Sign In') || bodyText.includes('邮箱')) {
    console.log('  Login form detected');
  } else {
    reportIssue(page, 'Login', 'Login page did not render correctly');
  }

  // Check for email input
  const emailInput = await page.$('input[placeholder*="邮箱"], input[type="email"], input[placeholder*="email"]');
  const passInput = await page.$('input[type="password"]');
  if (!emailInput) reportIssue(page, 'Login', 'Email input not found');
  if (!passInput) reportIssue(page, 'Login', 'Password input not found');

  // ===== 2. Login =====
  console.log('\n--- 2. Login Action ---');
  
  // First register via API
  const regRes = await fetch(`${PROD}/api/v1/users/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'testuser_prod@test.com', password: 'Test123456', username: 'prodtest' })
  }).catch(() => ({ status: 0 }));
  if (regRes.status === 200 || regRes.status === 201) console.log('  Registered test user');
  else console.log(`  Register: ${regRes.status} (user may exist)`);

  // Login via form
  if (emailInput && passInput) {
    await emailInput.fill('testuser_prod@test.com');
    await passInput.fill('Test123456');
    await screenshot(page, 'login-filled');

    const loginBtn = await page.$('button[type="submit"], button:has-text("登录")');
    if (loginBtn) {
      await loginBtn.click();
      await sleep(5000);
      await screenshot(page, 'after-login');
      const url = page.url();
      if (url.includes('/login')) {
        reportIssue(page, 'Login', 'Login did not redirect away from login page');
      } else {
        console.log(`  Login successful, redirected to: ${url}`);
        // Get token from localStorage
        token = await page.evaluate(() => localStorage.getItem('access_token') || localStorage.getItem('token') || '');
        console.log(`  Token: ${token ? token.substring(0, 20) + '...' : 'NOT FOUND'}`);
      }
    } else {
      reportIssue(page, 'Login', 'Login button not found');
    }
  }

  // ===== 3. Survey List Page =====
  console.log('\n--- 3. Survey List ---');
  await page.goto(`${PROD}/survey`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await screenshot(page, 'survey-list');

  const surveyText = await page.textContent('body').catch(() => '');
  const hasSurveyContent = surveyText.includes('调研') || surveyText.includes('问卷') || surveyText.includes('Survey');
  if (!hasSurveyContent) reportIssue(page, 'Survey List', 'Survey list page appears empty or broken');

  // Check for create button
  const createBtn = await page.$('button:has-text("新建"), button:has-text("创建"), button:has-text("新建调研")');
  if (createBtn) console.log('  Create survey button found');
  else reportIssue(page, 'Survey List', 'Create survey button not found');

  // ===== 4. Create Survey =====
  console.log('\n--- 4. Create Survey ---');
  if (createBtn) {
    await createBtn.click();
    await sleep(3000);
    await screenshot(page, 'create-survey-dialog');

    const titleInput = await page.$('input[placeholder*="标题"], input[placeholder*="title"], input[name="title"]');
    if (titleInput) {
      await titleInput.fill(`线上自动化测试问卷 ${Date.now()}`);
      const descInput = await page.$('textarea[placeholder*="描述"], textarea[placeholder*="description"]');
      if (descInput) await descInput.fill('Playwright线上自动化测试创建');
      await screenshot(page, 'survey-form-filled');

      const submitBtn = await page.$('.el-dialog button:has-text("确 定"), .el-dialog button:has-text("提交"), .el-dialog button:has-text("保存"), .el-dialog button:has-text("创建")');
      if (submitBtn) {
        await submitBtn.click({ force: true });
        await sleep(3000);
        await screenshot(page, 'after-create-survey');
      } else {
        // Try all dialog buttons
        const dialogBtns = await page.$$eval('.el-dialog__footer button, .el-dialog button', els =>
          els.map(e => ({ text: e.textContent.trim(), visible: e.offsetParent !== null }))
        );
        console.log(`  Dialog buttons: ${JSON.stringify(dialogBtns)}`);
        const anySubmit = await page.$('.el-dialog__footer button:last-child');
        if (anySubmit) await anySubmit.click({ force: true });
        await sleep(3000);
        await screenshot(page, 'after-create-survey-fallback');
      }
    } else {
      reportIssue(page, 'Create Survey', 'Title input not found in create dialog');
    }
  }

  // ===== 5. Analysis Page =====
  console.log('\n--- 5. Analysis Page ---');
  await page.goto(`${PROD}/analysis`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await screenshot(page, 'analysis-page');

  const analysisText = await page.textContent('body').catch(() => '');
  const hasAnalysisContent = analysisText.includes('分析') || analysisText.includes('Analytics') || analysisText.includes('统计');
  if (!hasAnalysisContent) reportIssue(page, 'Analysis', 'Analysis page appears empty or broken');

  // Check for chart/filter elements
  const selects = await page.$$('select, .el-select');
  console.log(`  Found ${selects.length} select/dropdown elements`);

  // ===== 6. Profile Page =====
  console.log('\n--- 6. Profile Page ---');
  await page.goto(`${PROD}/profile`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(3000);
  await screenshot(page, 'profile-page');

  // ===== 7. Navigation =====
  console.log('\n--- 7. Navigation ---');
  await page.goto(`${PROD}/`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(3000);

  const navLinks = await page.$$eval('nav a, .sidebar a, .menu a, [class*="nav"] a', links =>
    links.map(a => ({ text: a.textContent.trim().substring(0, 30), href: a.href }))
  ).catch(() => []);
  console.log(`  Nav links: ${JSON.stringify(navLinks.slice(0, 10))}`);

  // Click through each nav link
  for (const link of navLinks.slice(0, 6)) {
    if (!link.href || link.href === '#') continue;
    try {
      await page.goto(link.href, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(3000);
      const url = page.url();
      const hasError = url.includes('not-found') || url.includes('404');
      const pageTitle = await page.title().catch(() => '');
      console.log(`  Nav: ${link.text} -> ${url} (${hasError ? 'ERROR' : 'OK'})`);
      if (hasError) reportIssue(page, 'Navigation', `Page not found: ${link.text} (${link.href})`);
    } catch (e) {
      reportIssue(page, 'Navigation', `Failed to navigate to: ${link.text} - ${e.message}`);
    }
  }

  // ===== 8. Console Errors =====
  console.log('\n--- 8. Console Errors ---');
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.push(err.message));

  await page.goto(`${PROD}/survey`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);

  if (consoleErrors.length > 0) {
    consoleErrors.forEach(e => reportIssue(page, 'Console Error', e.substring(0, 200)));
  } else {
    console.log('  No console errors on survey page');
  }

  // ===== Summary =====
  console.log('\n\n========================================');
  console.log(`  ISSUES FOUND: ${issues.length}`);
  console.log('========================================');
  if (issues.length > 0) {
    issues.forEach((issue, i) => console.log(`  ${i + 1}. [${issue.area}] ${issue.description}`));
  } else {
    console.log('  All tests passed!');
  }

  await screenshot(page, 'final-state');
  console.log(`\nScreenshots saved to: ${SCREENSHOT_DIR}`);

  await browser.close();

  // Write issues to file for later use
  fs.writeFileSync(`${SCREENSHOT_DIR}/issues.json`, JSON.stringify(issues, null, 2));
  
  process.exit(issues.length > 0 ? 1 : 0);
})().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
