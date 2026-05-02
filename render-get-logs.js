const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  // Navigate directly to the service events page (shows deploys)
  const eventsUrl = 'https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/events';
  console.log('Opening events page:', eventsUrl);
  await page.goto(eventsUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await new Promise(r => setTimeout(r, 3000));
  
  const url = page.url();
  console.log('URL:', url);
  
  if (url.includes('login')) {
    console.log('需要登录！请在浏览器中登录 Render...');
    while (true) {
      await new Promise(r => setTimeout(r, 3000));
      try {
        const u = page.url();
        if (u.includes('dashboard.render.com') && !u.includes('login')) break;
      } catch (e) {}
    }
    await new Promise(r => setTimeout(r, 3000));
    await page.goto(eventsUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await new Promise(r => setTimeout(r, 5000));
  }

  await page.screenshot({ path: 're-1-events.png' });
  const eventsText = await page.textContent('body').catch(() => '');
  console.log('Events page text (first 4000):', eventsText.substring(0, 4000));

  // Find deploy-related links or buttons
  const links = await page.$$eval('a, button', els =>
    els.map(e => ({
      tag: e.tagName,
      text: e.textContent.trim().substring(0, 80),
      href: e.href || '',
      cls: (e.className || '').toString().substring(0, 40)
    })).filter(e => e.text.length > 0 && e.text.length < 80)
  ).catch(() => []);
  console.log('\nClickable elements:', JSON.stringify(links.slice(0, 30), null, 2));

  // Try clicking on any failed deploy event
  const failedEl = await page.$('text=build_failed') || await page.$('text=update_failed') || await page.$('text=failed');
  if (failedEl) {
    console.log('\nFound failed status, clicking...');
    await failedEl.click().catch(() => {});
    await new Promise(r => setTimeout(r, 5000));
    await page.screenshot({ path: 're-2-failed-detail.png' });
    const failText = await page.textContent('body').catch(() => '');
    console.log('Failed deploy detail:', failText.substring(0, 5000));
  }

  // Also check the logs page
  console.log('\nNavigating to logs page...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/logs', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 're-3-logs.png' });

  const logsText = await page.textContent('body').catch(() => '');
  console.log('Logs page text (first 5000):', logsText.substring(0, 5000));

  // Get log content from specific elements
  const logEls = await page.$$eval('pre, code, [class*="log"], [class*="Log"], [class*="line"], [class*="entry"], [class*="message"]', els =>
    els.map(e => ({ tag: e.tagName, cls: e.className.substring(0, 60), text: e.textContent.substring(0, 3000) }))
      .filter(e => e.text.length > 10)
  ).catch(() => []);
  if (logEls.length > 0) {
    console.log('\n=== LOG ENTRIES ===');
    logEls.forEach((l, i) => {
      console.log(`[${i}] ${l.cls}:`);
      console.log(l.text);
    });
  }

  // Go back to events and look for the manual deploy button
  console.log('\nNavigating back to service main page...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({ path: 're-4-main.png' });

  const mainText = await page.textContent('body').catch(() => '');
  console.log('Main page text (first 4000):', mainText.substring(0, 4000));

  // Look for Manual Deploy button
  const manualBtn = await page.$('button:has-text("Manual Deploy"), button:has-text("deploy"), button:has-text("Deploy")');
  if (manualBtn) {
    console.log('\nFound deploy button:', await manualBtn.textContent());
  }

  // Check settings page for current config
  console.log('\nChecking settings...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/settings', {
    waitUntil: 'domcontentloaded', timeout: 60000
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 're-5-settings.png' });

  const settingsText = await page.textContent('body').catch(() => '');
  console.log('Settings page text (first 6000):', settingsText.substring(0, 6000));

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
