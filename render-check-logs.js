const { chromium } = require('playwright');
const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';
const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await ctx.newPage();

  // LOGIN
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
    try { const u = page.url(); if (u.includes('dashboard.render.com') && !u.includes('login')) break; } catch(e){}
  }
  await sleep(3000);
  console.log('Logged in!');

  // Go to events page
  console.log('Navigating to events...');
  await page.goto(`https://dashboard.render.com/web/${SERVICE_ID}/events`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await page.screenshot({ path: 're-events.png' });

  // Get page text
  const text = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('Events text (first 4000):', text.substring(0, 4000));

  // Find and click on the latest deploy event
  const deployLinks = await page.$$eval('a, [role="button"], button', els =>
    els.map(e => ({ text: e.textContent.trim().substring(0, 80), href: e.getAttribute('href') || '' }))
      .filter(e => e.href.includes('dep-') || /failed|deploy/i.test(e.text))
  ).catch(() => []);
  console.log('\nDeploy-related elements:', JSON.stringify(deployLinks.slice(0, 10), null, 2));

  // Try clicking on the latest failed deploy
  const failedLink = await page.$('a[href*="dep-d7nf9h3"]');
  if (failedLink) {
    await failedLink.click().catch(() => {});
    await sleep(5000);
    await page.screenshot({ path: 're-deploy-detail.png' });
    const detail = await page.evaluate(() => document.body.innerText).catch(() => '');
    console.log('\nDeploy detail (first 5000):', detail.substring(0, 5000));
  }

  // Try the logs page directly
  console.log('\nChecking logs page...');
  await page.goto(`https://dashboard.render.com/web/${SERVICE_ID}/logs`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await page.screenshot({ path: 're-logs.png' });

  const logsText = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('Logs text (first 5000):', logsText.substring(0, 5000));

  // Get log entries
  const logEls = await page.$$eval('pre, code, [class*="log"], [class*="Log"], [class*="line"], [class*="entry"]', els =>
    els.map(e => e.textContent.substring(0, 3000)).filter(t => t.length > 10)
  ).catch(() => []);
  if (logEls.length > 0) {
    console.log('\n=== LOG ENTRIES ===');
    logEls.forEach((t, i) => console.log(`[${i}]: ${t}`));
  }

  console.log('\nBrowser stays open.');
  await new Promise(() => {});
})().catch(err => { console.error('Error:', err.message); process.exit(1); });
