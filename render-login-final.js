const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  console.log('Step 1: Opening Render login page...');
  await page.goto('https://dashboard.render.com/login', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await new Promise(r => setTimeout(r, 3000));
  console.log('URL:', page.url());

  // Fill email
  const emailInput = await page.$('input[type="email"], input[name="email"]');
  const passInput = await page.$('input[type="password"]');
  
  console.log('Email field found:', !!emailInput);
  console.log('Password field found:', !!passInput);

  if (emailInput) await emailInput.fill('he2827987@gmail.com');
  if (passInput) await passInput.fill('Heyang@42507002');
  await page.screenshot({ path: 'rl-1-filled.png' });

  // Click sign in
  const submitBtn = await page.$('button[type="submit"]');
  if (submitBtn) {
    console.log('Clicking Sign In...');
    await submitBtn.click({ noWaitAfter: true }).catch(() => {});
  }

  // Wait for dashboard
  console.log('Waiting for dashboard...');
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 3000));
    try {
      const u = page.url();
      if (u.includes('dashboard.render.com') && !u.includes('login') && !u.includes('sign')) {
        console.log('Login success! URL:', u);
        break;
      }
    } catch (e) {}
  }

  await new Promise(r => setTimeout(r, 3000));
  console.log('Current URL:', page.url());
  await page.screenshot({ path: 'rl-2-logged-in.png' });

  // Navigate to service events/deploys
  console.log('\nStep 2: Going to service page...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'rl-3-service.png' });
  const svcText = await page.textContent('body').catch(() => '');
  console.log('Service page (first 3000):', svcText.substring(0, 3000));

  // Go to events page to see deploys
  console.log('\nStep 3: Going to events...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/events', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'rl-4-events.png' });
  const evtText = await page.textContent('body').catch(() => '');
  console.log('Events text (first 4000):', evtText.substring(0, 4000));

  // Look for deploy events and click the first one
  const deployLinks = await page.$$eval('a, button, [role="button"], [class*="event"], [class*="deploy"]', els =>
    els.filter(e => /deploy|build|fail/i.test(e.textContent) || /deploy/i.test(e.getAttribute('href') || ''))
      .map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 100), href: e.getAttribute('href') || '' }))
  ).catch(() => []);
  console.log('\nDeploy-related elements:', JSON.stringify(deployLinks.slice(0, 10), null, 2));

  // Try clicking on first failed deploy
  const firstDeploy = await page.$('a[href*="dep-"]');
  if (firstDeploy) {
    console.log('\nClicking first deploy...');
    await firstDeploy.click().catch(() => {});
    await new Promise(r => setTimeout(r, 5000));
    await page.screenshot({ path: 'rl-5-deploy-detail.png' });
    const detailText = await page.textContent('body').catch(() => '');
    console.log('Deploy detail (first 5000):', detailText.substring(0, 5000));

    // Try to get log output
    const logEls = await page.$$eval('pre, code, [class*="log"], [class*="Log"], [class*="terminal"], [class*="output"], [class*="line"]', els =>
      els.map(e => ({ tag: e.tagName, cls: e.className.substring(0, 50), text: e.textContent.substring(0, 5000) }))
        .filter(e => e.text.length > 5)
    ).catch(() => []);
    if (logEls.length > 0) {
      console.log('\n=== BUILD LOGS ===');
      logEls.forEach((l, i) => console.log(`\n[${i}] ${l.tag}.${l.cls}:\n${l.text}`));
    }
  }

  // Also check logs page for recent output
  console.log('\nStep 4: Checking logs page...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/logs', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'rl-6-logs.png' });
  const logsPageText = await page.textContent('body').catch(() => '');
  console.log('Logs page (first 5000):', logsPageText.substring(0, 5000));

  const logEntries = await page.$$eval('pre, code, [class*="log"], [class*="Log"], [class*="line"], [class*="entry"], [class*="message"]', els =>
    els.map(e => e.textContent.substring(0, 3000)).filter(t => t.length > 5)
  ).catch(() => []);
  if (logEntries.length > 0) {
    console.log('\n=== LOG ENTRIES ===');
    logEntries.forEach((t, i) => console.log(`[${i}]: ${t}`));
  }

  // Save browser state for reuse
  console.log('\n=== DONE ===');
  console.log('Browser stays open.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
