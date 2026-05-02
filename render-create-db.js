const { chromium } = require('playwright');

const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';
const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 150 });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await ctx.newPage();

  // ===== LOGIN =====
  console.log('1. Login to Render...');
  await page.goto('https://dashboard.render.com/login', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await sleep(3000);

  const email = await page.$('input[type="email"], input[name="email"]');
  const pass = await page.$('input[type="password"]');
  if (email && pass) {
    await email.fill('he2827987@gmail.com');
    await pass.fill('Heyang@42507002');
    const btn = await page.$('button[type="submit"]');
    if (btn) await btn.click({ noWaitAfter: true }).catch(() => {});
  }

  for (let i = 0; i < 80; i++) {
    await sleep(3000);
    try {
      const u = page.url();
      if (u.includes('dashboard.render.com') && !u.includes('login') && !u.includes('sign')) {
        console.log('   Logged in!');
        break;
      }
    } catch (e) {}
  }
  await sleep(3000);

  // ===== CLICK "NEW" BUTTON TO OPEN MENU =====
  console.log('\n2. Clicking New button...');
  // There are two "New" buttons - click the one in the top nav
  const newButtons = await page.$$('button');
  let clicked = false;
  for (const btn of newButtons) {
    const text = (await btn.textContent().catch(() => '')).trim();
    if (text === 'New') {
      await btn.click().catch(() => {});
      console.log('   Clicked New button');
      clicked = true;
      break;
    }
  }
  if (!clicked) {
    console.log('   Could not find New button');
  }
  await sleep(2000);
  await page.screenshot({ path: 'rd-1-new-menu.png' });

  // ===== FIND AND CLICK "PostgreSQL" OPTION =====
  console.log('\n3. Looking for PostgreSQL option...');
  // The dropdown menu should have options - find them
  const menuText = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('   Menu text snippet:', menuText.substring(0, 500));

  // Look for PostgreSQL link/button in the dropdown
  const pgOption = await page.$('text=PostgreSQL') || await page.$('a:has-text("PostgreSQL")') || await page.$('button:has-text("PostgreSQL")');
  if (pgOption) {
    console.log('   Found PostgreSQL option, clicking...');
    await pgOption.click().catch(() => {});
    await sleep(5000);
  } else {
    console.log('   PostgreSQL option not found in dropdown, trying direct URL...');
    await page.goto('https://dashboard.render.com/new/postgres', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(5000);
  }

  await page.screenshot({ path: 'rd-2-pg-page.png' });
  const pgText = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('   PostgreSQL page text (first 2000):', pgText.substring(0, 2000));

  // ===== FILL DATABASE FORM =====
  console.log('\n4. Filling database creation form...');

  // List all input fields
  const inputs = await page.$$eval('input, select', els =>
    els.map(e => ({
      tag: e.tagName, type: e.type, name: e.name, id: e.id,
      placeholder: e.placeholder,
      label: e.closest('label')?.textContent?.trim()?.substring(0, 50) || '',
      ariaLabel: e.getAttribute('aria-label') || '',
      value: (e.value || '').substring(0, 30)
    })).filter(e => e.type !== 'checkbox' && e.type !== 'hidden')
  ).catch(() => []);
  console.log('   Form inputs:', JSON.stringify(inputs, null, 2));

  // Try to find and fill the name field
  for (const sel of [
    'input[name="name"]', 'input[placeholder*="Name"]', 'input[aria-label*="name"]',
    'input[aria-label*="Name"]', '#name'
  ]) {
    const inp = await page.$(sel);
    if (inp) {
      await inp.fill('survey-product-db');
      console.log('   Filled name via', sel);
      break;
    }
  }

  // Try to find and fill database name
  for (const sel of [
    'input[name="databaseName"]', 'input[placeholder*="Database"]',
    'input[aria-label*="Database"]', '#databaseName'
  ]) {
    const inp = await page.$(sel);
    if (inp) {
      await inp.fill('surveyproduct_db');
      console.log('   Filled database name via', sel);
      break;
    }
  }

  // Try to find and fill user
  for (const sel of [
    'input[name="user"]', 'input[placeholder*="User"]',
    'input[aria-label*="User"]', '#user'
  ]) {
    const inp = await page.$(sel);
    if (inp) {
      await inp.fill('surveyproduct_db_user');
      console.log('   Filled user via', sel);
      break;
    }
  }

  // Select Free plan
  const freePlanBtn = await page.$('text=Free') || await page.$('[data-testid*="free"]');
  if (freePlanBtn) {
    await freePlanBtn.click().catch(() => {});
    console.log('   Selected Free plan');
  }

  // Select Oregon region
  const regionDropdown = await page.$('select[name="region"], select[aria-label*="region"], select[aria-label*="Region"]');
  if (regionDropdown) {
    await regionDropdown.selectOption({ label: 'Oregon' }).catch(() => {});
    console.log('   Selected Oregon');
  }

  await page.screenshot({ path: 'rd-3-form-filled.png' });

  // Find and click Create/Apply button
  console.log('\n5. Looking for Create button...');
  const buttons = await page.$$eval('button', els =>
    els.map(e => ({ text: e.textContent.trim().substring(0, 60), type: e.type, disabled: e.disabled }))
  ).catch(() => []);
  console.log('   Buttons:', JSON.stringify(buttons, null, 2));

  const createBtn = await page.$('button:has-text("Create Database")') ||
                    await page.$('button:has-text("Create")') ||
                    await page.$('button:has-text("Apply")');
  if (createBtn) {
    const btnText = await createBtn.textContent().catch(() => '');
    console.log('   Clicking:', btnText.trim());
    await createBtn.click().catch(() => {});
    await sleep(10000);
    await page.screenshot({ path: 'rd-4-after-create.png' });
    console.log('   URL after create:', page.url());
  }

  // ===== WAIT FOR DATABASE AND GET CONNECTION STRING =====
  console.log('\n6. Waiting for database to be created...');
  const dbPageText = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('   Page text (first 3000):', dbPageText.substring(0, 3000));

  // Look for connection string on the page
  const connStr = dbPageText.match(/postgresql:\/\/[^\s"<>]+/)?.[0];
  if (connStr) {
    console.log('\n   *** FOUND CONNECTION STRING ***');
    console.log('   ', connStr);
  }

  // Check all text content for any connection info
  const fullText = await page.evaluate(() => {
    const allElements = document.querySelectorAll('*');
    let result = '';
    for (const el of allElements) {
      if (el.children.length === 0 && el.textContent.includes('postgresql')) {
        result += el.textContent + '\n';
      }
    }
    return result;
  }).catch(() => '');
  if (fullText) {
    console.log('   PostgreSQL references:', fullText);
  }

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
