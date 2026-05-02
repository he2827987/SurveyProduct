const { chromium } = require('playwright');
const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';
const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
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

  // Go to the latest deploy logs
  console.log('Navigating to latest deploy...');
  
  // First get the latest deploy ID via API
  const deployRes = await fetch(`https://api.render.com/v1/services/${SERVICE_ID}/deploys?limit=1`, {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
  const deployData = await deployRes.json();
  const deployId = deployData[0]?.deploy?.id;
  console.log('Latest deploy:', deployId);

  // Navigate to the deploy page
  await page.goto(`https://dashboard.render.com/web/${SERVICE_ID}/deploys/${deployId}`, {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await sleep(5000);

  // Wait for deploy to finish (keep checking)
  console.log('Waiting for deploy to finish...');
  for (let i = 0; i < 30; i++) {
    await sleep(10000);
    const statusRes = await fetch(`https://api.render.com/v1/services/${SERVICE_ID}/deploys/${deployId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const status = (await statusRes.json()).status;
    console.log(`[${i*10}s] Status: ${status}`);
    if (['live', 'update_failed', 'build_failed', 'canceled'].includes(status)) break;
  }

  await sleep(3000);
  await page.screenshot({ path: 'rd-deploy-logs.png' });

  // Get all text from the deploy page
  const text = await page.evaluate(() => document.body.innerText).catch(() => '');
  console.log('\n=== DEPLOY PAGE TEXT ===');
  console.log(text.substring(0, 8000));
  
  // Look for config/debug output specifically
  const configLines = text.split('\n').filter(l => l.includes('[Config]') || l.includes('DATABASE_URL') || l.includes('ENVIRONMENT'));
  console.log('\n=== CONFIG LINES ===');
  configLines.forEach(l => console.log(l.trim()));

  // Look for error lines
  const errorLines = text.split('\n').filter(l => l.includes('Error') || l.includes('error') || l.includes('Traceback') || l.includes('Failed'));
  console.log('\n=== ERROR LINES ===');
  errorLines.forEach(l => console.log(l.trim()));

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => { console.error('Error:', err.message); process.exit(1); });
