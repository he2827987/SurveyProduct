const { chromium } = require('playwright');
const PROD = 'https://surveyproduct.onrender.com';
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const pages = [
    { name: 'Login', url: '/login' },
    { name: 'Dashboard', url: '/dashboard' },
    { name: 'Survey List', url: '/survey' },
    { name: 'Analysis', url: '/analysis' },
    { name: 'Profile', url: '/profile' },
  ];

  const issues = [];

  for (const p of pages) {
    console.log(`\n=== ${p.name}: ${p.url} ===`);
    try {
      const resp = await page.goto(`${PROD}${p.url}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
      console.log(`HTTP: ${resp.status()}`);
      await sleep(8000);

      const url = page.url();
      console.log(`Final URL: ${url}`);

      const html = await page.evaluate(() => {
        const getVisibleText = () => {
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
          let text = '';
          while (walker.nextNode()) {
            const n = walker.currentNode;
            if (n.parentElement && n.parentElement.offsetParent !== null && n.textContent.trim()) {
              text += n.textContent.trim() + ' ';
            }
          }
          return text.substring(0, 2000);
        };
        return {
          title: document.title,
          bodyText: getVisibleText(),
          inputs: Array.from(document.querySelectorAll('input, textarea, select')).map(e => ({
            type: e.type || e.tagName, placeholder: e.placeholder, name: e.name,
            visible: e.offsetParent !== null, value: (e.value || '').substring(0, 30)
          })),
          buttons: Array.from(document.querySelectorAll('button')).map(e => ({
            text: e.textContent.trim().substring(0, 50), visible: e.offsetParent !== null, disabled: e.disabled
          })),
          links: Array.from(document.querySelectorAll('a')).filter(a => a.offsetParent !== null).map(a => ({
            text: a.textContent.trim().substring(0, 40), href: a.href
          })),
          errors: Array.from(document.querySelectorAll('.el-message, [role="alert"], .error')).map(e => e.textContent.trim())
        };
      });

      console.log(`Title: ${html.title}`);
      console.log(`Text (first 500): ${html.bodyText.substring(0, 500)}`);
      console.log(`Inputs (${html.inputs.length}): ${JSON.stringify(html.inputs.filter(i => i.visible).slice(0, 5))}`);
      console.log(`Buttons (${html.buttons.length}): ${JSON.stringify(html.buttons.filter(b => b.visible).slice(0, 10))}`);
      console.log(`Links (${html.links.length}): ${JSON.stringify(html.links.slice(0, 8))}`);
      if (html.errors.length) console.log(`Errors: ${JSON.stringify(html.errors)}`);

      // Check for issues
      if (url.includes('/login') && p.url !== '/login') {
        issues.push({ page: p.name, issue: `Redirected to login (not authenticated for ${p.url})` });
      }
      if (html.bodyText.length < 20 && p.url !== '/login') {
        issues.push({ page: p.name, issue: 'Page appears empty' });
      }
    } catch (e) {
      console.log(`Error: ${e.message}`);
      issues.push({ page: p.name, issue: e.message });
    }
  }

  // Login and retry protected pages
  console.log('\n\n=== Logging in and retrying ===');
  await page.goto(`${PROD}/login`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);

  const emailInput = await page.$('input[placeholder*="邮箱"], input[type="email"]');
  const passInput = await page.$('input[type="password"]');
  if (emailInput && passInput) {
    await emailInput.fill('testuser_prod@test.com');
    await passInput.fill('Test123456');
    const btn = await page.$('button[type="submit"]');
    if (btn) await btn.click({ force: true });
    await sleep(5000);
    console.log(`After login URL: ${page.url()}`);
  }

  // Re-check pages after login
  for (const p of [{ name: 'Survey (logged in)', url: '/survey' }, { name: 'Analysis (logged in)', url: '/analysis' }]) {
    console.log(`\n=== ${p.name} ===`);
    await page.goto(`${PROD}${p.url}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(5000);
    const url = page.url();
    const text = await page.evaluate(() => document.body.innerText.substring(0, 1500));
    const buttons = await page.$$eval('button', els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim().substring(0, 40)));
    const inputs = await page.$$eval('input, select', els => els.filter(e => e.offsetParent !== null).map(e => `${e.type||e.tagName}:${e.placeholder||e.name||''}`));
    console.log(`URL: ${url}`);
    console.log(`Text: ${text.substring(0, 300)}`);
    console.log(`Buttons: ${JSON.stringify(buttons)}`);
    console.log(`Inputs: ${JSON.stringify(inputs)}`);

    if (url.includes('/login')) issues.push({ page: p.name, issue: 'Still redirected to login' });
  }

  console.log('\n\n========================================');
  console.log(`ISSUES: ${issues.length}`);
  issues.forEach((issue, i) => console.log(`  ${i + 1}. [${issue.page}] ${issue.issue}`));
  console.log('========================================');

  await browser.close();
})();
