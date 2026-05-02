const { chromium, devices } = require('playwright');

const PROD = 'https://surveyproduct.onrender.com';
const EMAIL = 'prodtest2@test.com';
const PASS = 'Test123456';

const results = { pass: [], fail: [] };
function log(msg) { console.log(`  ${msg}`); }
function ok(msg) { results.pass.push(msg); log(`✅ ${msg}`); }
function fail(msg) { results.fail.push(msg); log(`❌ ${msg}`); }

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('pageerror', e => log(`PageErr: ${e.message.substring(0, 100)}`));
  page.on('console', msg => {
    if (msg.type() === 'error') log(`Console: ${msg.text().substring(0, 120)}`);
  });

  // ===== LOGIN =====
  console.log('\n=== LOGIN ===');
  await page.goto(`${PROD}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.fill('input[placeholder*="邮箱"]', EMAIL);
  await page.fill('input[type="password"]', PASS);
  await page.locator('button:has-text("登录")').click();
  await page.waitForURL('**/dashboard**', { timeout: 15000 });
  await page.waitForTimeout(2000);
  ok('Logged in');

  // ===== NAVIGATE TO QUESTION BANK =====
  console.log('\n=== QUESTION BANK ===');
  await page.locator('.el-menu-item').filter({ hasText: '题库管理' }).first().click();
  await page.waitForTimeout(3000);
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await page.screenshot({ path: 'e2e-01-question-bank.png' });
  const qbContent = await page.textContent('body');
  if (qbContent.includes('题库') || qbContent.includes('问题')) ok('Question bank page loaded');
  else fail('Question bank page not loaded');

  // Check for "create question" button
  const createBtn = page.locator('button:has-text("新增"), button:has-text("创建"), button:has-text("添加题目")').first();
  const hasCreateBtn = await createBtn.count();
  if (hasCreateBtn > 0) {
    ok('Create question button found');
    await createBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'e2e-02-create-question-dialog.png' });
  } else {
    fail('No create question button found');
  }

  // Check if dialog/form appeared
  const dialog = page.locator('.el-dialog, .el-drawer, .el-form:visible, [role="dialog"]').first();
  const hasDialog = await dialog.count();
  if (hasDialog === 0) {
    // Maybe it's inline form
    const form = page.locator('.question-form, .create-form, form').first();
    const hasForm = await form.count();
    if (hasForm === 0) {
      log('No dialog or form found. Page content preview:');
      const text = await page.textContent('body').catch(() => '');
      log(text.substring(0, 500));
    }
  }

  // Check what UI elements are available
  const allButtons = await page.locator('button').evaluateAll(els =>
    els.map(e => ({ text: e.textContent.trim().substring(0, 40), visible: e.offsetParent !== null }))
  );
  log('All visible buttons:');
  for (const b of allButtons) {
    if (b.visible) log(`  [btn] "${b.text}"`);
  }

  // Check for add button icon
  const addBtn = page.locator('.el-button--primary:visible').first();
  const addBtnText = await addBtn.textContent().catch(() => '');
  log(`Primary button text: "${addBtnText}"`);

  await page.screenshot({ path: 'e2e-03-question-bank-full.png' });

  // Close dialog if open
  const cancelBtn = page.locator('button:has-text("取消")').first();
  if (await cancelBtn.count() > 0) {
    await cancelBtn.click().catch(() => {});
    await page.waitForTimeout(500);
  }
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(500);

  // ===== NAVIGATE TO SURVEY PAGE =====
  console.log('\n=== SURVEY MANAGEMENT ===');
  await page.locator('.el-menu-item').filter({ hasText: '调研管理' }).first().click();
  await page.waitForTimeout(3000);
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await page.screenshot({ path: 'e2e-04-survey-page.png' });
  const surveyContent = await page.textContent('body');
  if (surveyContent.includes('调研')) ok('Survey page loaded');
  else fail('Survey page not loaded');

  // Check for create survey button
  const surveyBtns = await page.locator('button:visible').evaluateAll(els =>
    els.map(e => e.textContent.trim().substring(0, 40))
  );
  log('Survey page buttons:');
  for (const b of surveyBtns) {
    log(`  "${b}"`);
  }

  // ===== NAVIGATE TO ANALYSIS PAGE =====
  console.log('\n=== ANALYSIS PAGE ===');
  await page.locator('.el-menu-item').filter({ hasText: '数据分析' }).first().click();
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'e2e-05-analysis-page.png' });

  // Check survey dropdown
  await page.locator('.filter-select, .el-select').first().click().catch(() => {});
  await page.waitForTimeout(1000);
  const dropdownItems = await page.locator('.el-select-dropdown__item:visible').count();
  if (dropdownItems > 0) {
    ok(`Analysis page has ${dropdownItems} surveys in dropdown`);
    const items = await page.locator('.el-select-dropdown__item:visible').evaluateAll(els =>
      els.map(e => e.textContent.trim().substring(0, 50))
    );
    for (const item of items.slice(0, 5)) {
      log(`  Survey: "${item}"`);
    }
  } else {
    log('No dropdown items found (might need to click differently)');
  }

  // Click elsewhere to close dropdown
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // ===== SUMMARY =====
  console.log('\n==========================================');
  console.log(`  RESULTS: ${results.pass.length} passed, ${results.fail.length} failed`);
  if (results.fail.length > 0) {
    console.log('  Failed:');
    results.fail.forEach(f => log(`    ❌ ${f}`));
  }
  console.log('==========================================');

  await browser.close();
})();
