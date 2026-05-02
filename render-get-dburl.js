const { chromium } = require('playwright');
const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';
const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';
const DB_ID = 'dpg-d7negmsvikkc73b7j52g-a';

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
  console.log('1. Login...');
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
      if (u.includes('dashboard.render.com') && !u.includes('login') && !u.includes('sign')) break;
    } catch (e) {}
  }
  await sleep(3000);
  console.log('   Logged in!');

  // NAVIGATE TO DATABASE PAGE
  const dbUrl = `https://dashboard.render.com/d/${DB_ID}`;
  console.log('\n2. Opening database page:', dbUrl);
  await page.goto(dbUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);
  await page.screenshot({ path: 'rd-db-1.png' });

  const dbText = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('   DB page text (first 4000):', dbText.substring(0, 4000));

  // Look for connection strings
  const pgUrls = dbText.match(/postgresql:\/\/[^\s"<>]+/g);
  if (pgUrls) {
    console.log('\n   *** PostgreSQL URLs found ***');
    pgUrls.forEach((u, i) => console.log(`   [${i}] ${u}`));
  }

  // Also check for individual connection fields (host, port, database, user, password)
  const connFields = await page.$$eval('*', els => {
    const result = {};
    for (const el of els) {
      const text = el.textContent?.trim() || '';
      if (el.children.length < 3) {
        if (/Hostname|Host|host/i.test(text) && text.length < 200) result.host = text;
        if (/Port|port/i.test(text) && text.length < 200) result.port = text;
        if (/Database|database/i.test(text) && text.length < 200 && !text.includes('Database Name')) result.database = text;
        if (/Username|User/i.test(text) && text.length < 200) result.user = text;
        if (/Password|password/i.test(text) && text.length < 200) result.password = text;
      }
    }
    return result;
  }).catch(() => ({}));
  console.log('\n   Connection fields:', JSON.stringify(connFields, null, 2));

  // Try to find and click on "Connection Info" or "Connect" button/tab
  const connBtn = await page.$('a:has-text("Connection"), button:has-text("Connection"), a:has-text("Connect"), button:has-text("Connect")');
  if (connBtn) {
    console.log('\n   Clicking Connection/Connect...');
    await connBtn.click().catch(() => {});
    await sleep(3000);
    await page.screenshot({ path: 'rd-db-2-conn.png' });
    const connText = await page.evaluate(() => document.body.innerText).catch(() => '');
    console.log('   Connection page text (first 4000):', connText.substring(0, 4000));
    
    const urls2 = connText.match(/postgresql:\/\/[^\s"<>]+/g);
    if (urls2) {
      console.log('\n   *** PostgreSQL URLs on connection page ***');
      urls2.forEach((u, i) => console.log(`   [${i}] ${u}`));
    }
  }

  // Look for all text containing "dpg-" (database host)
  const dpgRefs = await page.$$eval('*', els => {
    const results = new Set();
    for (const el of els) {
      const text = el.textContent || '';
      const matches = text.match(/dpg-[a-z0-9-]+/g);
      if (matches) matches.forEach(m => results.add(m));
    }
    return [...results];
  }).catch(() => []);
  console.log('\n   dpg references:', dpgRefs);

  // Try the internal connection URL format
  // For Render PostgreSQL: the internal host is dpg-<id>.render.com
  console.log('\n   Expected internal host: dpg-d7negmsvikkc73b7j52g.oregon-postgres.render.com');
  console.log('   Expected external host: dpg-d7negmsvikkc73b7j52g-a.oregon-postgres.render.com');

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
