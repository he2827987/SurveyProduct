const { chromium } = require('playwright');

const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';
const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';

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

  // LIST ALL SERVICES TO FIND DATABASE
  console.log('\n2. Looking for database service...');
  await page.goto('https://dashboard.render.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(5000);

  // Get all links that might be database services
  const allLinks = await page.$$eval('a', as =>
    as.map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 80) }))
      .filter(l => l.href.includes('dpg-') || l.href.includes('database') || l.text.toLowerCase().includes('db') || l.text.toLowerCase().includes('survey'))
  ).catch(() => []);
  console.log('   DB-related links:', JSON.stringify(allLinks, null, 2));

  // Try to find the database link by looking for dpg- pattern in all links
  const dbLinks = await page.$$eval('a[href*="/dpg-"]', as =>
    as.map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 80) }))
  ).catch(() => []);
  console.log('   dpg links:', JSON.stringify(dbLinks, null, 2));

  // If no dpg links, try to navigate via the "New" dropdown to find databases
  // Or look at all service links
  const svcLinks = await page.$$eval('a', as =>
    as.map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 80) }))
      .filter(l => l.href.includes('dashboard.render.com/') && l.href.split('/').length > 4)
  ).catch(() => []);
  console.log('   Service links:', JSON.stringify(svcLinks.slice(0, 10), null, 2));

  // Try clicking on the database service if found
  if (dbLinks.length > 0) {
    console.log('\n3. Clicking database link...');
    await page.goto(dbLinks[0].href, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(5000);
    await page.screenshot({ path: 'rd-db-page.png' });
    
    const dbPageText = await page.evaluate(() => document.body.innerText).catch(() => '');
    console.log('   DB page text (first 3000):', dbPageText.substring(0, 3000));

    // Look for Internal Database URL or External Database URL
    const pgUrls = dbPageText.match(/postgresql:\/\/[^\s"<>]+/g);
    if (pgUrls && pgUrls.length > 0) {
      console.log('\n   *** FOUND POSTGRESQL URLs ***');
      pgUrls.forEach((u, i) => console.log(`   [${i}] ${u}`));
    }

    // Also try to get connection info from specific elements
    const connInfo = await page.$$eval('*', els => {
      const results = [];
      for (const el of els) {
        const text = el.textContent || '';
        if (text.includes('postgresql://') && el.children.length < 3) {
          results.push(text.trim().substring(0, 200));
        }
      }
      return results;
    }).catch(() => []);
    if (connInfo.length > 0) {
      console.log('\n   Connection info elements:');
      connInfo.forEach((t, i) => console.log(`   [${i}] ${t}`));
    }

    // Check for a "Connection" tab or section
    const connLink = await page.$('a:has-text("Connection"), button:has-text("Connection"), text=Connection Info');
    if (connLink) {
      console.log('\n   Clicking Connection tab...');
      await connLink.click().catch(() => {});
      await sleep(3000);
      await page.screenshot({ path: 'rd-db-connection.png' });
      const connText = await page.evaluate(() => document.body.innerText).catch(() => '');
      console.log('   Connection text (first 3000):', connText.substring(0, 3000));
    }
  } else {
    // Try to find the database via API
    console.log('\n3. Trying to find database via API...');
    const { execSync } = require('child_process');
    const svcList = execSync(
      `curl -s -H "Authorization: Bearer ${API_KEY}" "https://api.render.com/v1/services?limit=20"`,
      { encoding: 'utf-8' }
    );
    const services = JSON.parse(svcList);
    for (const item of services) {
      const s = item.service || item;
      console.log(`   ${s.type} | ${s.name} | ${s.id}`);
    }
  }

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
