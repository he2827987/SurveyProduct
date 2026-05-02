const { chromium } = require('playwright');

const PROD_URL = 'https://surveyproduct.onrender.com';
const TEST_EMAIL = 'testuser_prod@test.com';
const TEST_PASSWORD = 'Test123456';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const requests = [];
  const responses = [];
  const consoleMessages = [];
  const errors = [];

  page.on('request', req => {
    if (req.url().includes('surveyproduct') || req.url().includes('api')) {
      requests.push({
        url: req.url(),
        method: req.method(),
        headers: req.headers(),
        postData: req.postData()?.substring(0, 500),
      });
    }
  });

  page.on('response', async res => {
    if (res.url().includes('surveyproduct') || res.url().includes('api')) {
      let body = null;
      try {
        body = await res.text().catch(() => 'N/A');
        if (body && body.length > 500) body = body.substring(0, 500) + '...';
      } catch (e) {
        body = 'Could not read body';
      }
      responses.push({
        url: res.url(),
        status: res.status(),
        statusText: res.statusText(),
        headers: res.headers(),
        body: body,
      });
    }
  });

  page.on('console', msg => {
    consoleMessages.push({ type: msg.type(), text: msg.text() });
  });

  page.on('pageerror', err => {
    errors.push(err.message);
  });

  console.log('=== Step 1: Navigate to login page ===');
  await page.goto(`${PROD_URL}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  console.log('Current URL:', page.url());

  await page.screenshot({ path: 'diag-01-login-page.png' });

  console.log('\n=== Step 2: Check page content ===');
  const h2 = await page.textContent('h2').catch(() => 'NOT FOUND');
  console.log('Title h2:', h2);

  const inputs = await page.locator('input').count();
  console.log('Number of inputs:', inputs);

  const buttons = await page.locator('button').count();
  console.log('Number of buttons:', buttons);

  const allInputTypes = await page.locator('input').evaluateAll(els =>
    els.map(e => ({ type: e.type, placeholder: e.placeholder, visible: e.offsetParent !== null }))
  );
  console.log('Input details:', JSON.stringify(allInputTypes, null, 2));

  console.log('\n=== Step 3: Fill in login form ===');
  const emailInput = page.locator('input[placeholder*="邮箱"]');
  const passwordInput = page.locator('input[type="password"]');

  await emailInput.fill(TEST_EMAIL);
  await passwordInput.fill(TEST_PASSWORD);
  console.log('Filled email and password');

  await page.screenshot({ path: 'diag-02-filled.png' });

  console.log('\n=== Step 4: Click login button ===');
  const loginBtn = page.locator('button:has-text("登录")');
  await loginBtn.click();
  console.log('Login button clicked');

  console.log('\n=== Step 5: Wait and observe ===');
  await page.waitForTimeout(8000);

  console.log('Current URL after login:', page.url());
  await page.screenshot({ path: 'diag-03-after-login.png' });

  const token = await page.evaluate(() => localStorage.getItem('access_token'));
  console.log('Token in localStorage:', token ? token.substring(0, 50) + '...' : 'NOT FOUND');

  const userInfo = await page.evaluate(() => localStorage.getItem('user_info'));
  console.log('User info in localStorage:', userInfo);

  console.log('\n=== Network Requests ===');
  requests.forEach((r, i) => {
    console.log(`\nRequest ${i + 1}:`);
    console.log(`  ${r.method} ${r.url}`);
    if (r.postData) console.log(`  PostData: ${r.postData.substring(0, 300)}`);
    const ct = r.headers['content-type'];
    if (ct) console.log(`  Content-Type: ${ct}`);
  });

  console.log('\n=== Network Responses ===');
  responses.forEach((r, i) => {
    console.log(`\nResponse ${i + 1}:`);
    console.log(`  ${r.status} ${r.statusText} ${r.url}`);
    const ct = r.headers['content-type'];
    if (ct) console.log(`  Content-Type: ${ct}`);
    if (r.body) console.log(`  Body: ${r.body.substring(0, 300)}`);
  });

  console.log('\n=== Console Messages ===');
  consoleMessages.forEach(m => {
    if (m.type === 'error' || m.type === 'warning' || m.text.includes('登录') || m.text.includes('token') || m.text.includes('错误')) {
      console.log(`[${m.type}] ${m.text}`);
    }
  });

  console.log('\n=== Page Errors ===');
  if (errors.length === 0) {
    console.log('No page errors');
  } else {
    errors.forEach(e => console.log(e));
  }

  console.log('\n=== DOM check: any error messages visible? ===');
  const elMessages = await page.locator('.el-message').count();
  console.log('Element Plus messages visible:', elMessages);
  if (elMessages > 0) {
    for (let i = 0; i < elMessages; i++) {
      const text = await page.locator('.el-message').nth(i).textContent();
      console.log(`  Message ${i}: ${text}`);
    }
  }

  await browser.close();
  console.log('\n=== Done ===');
})();
