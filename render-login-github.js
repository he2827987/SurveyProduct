const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 200 });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  // Step 1: Go to Render login
  console.log('Step 1: Opening Render login page...');
  await page.goto('https://dashboard.render.com/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({ path: 'r1-login.png' });

  // Step 2: Click GitHub login button
  console.log('Step 2: Clicking GitHub login...');
  const githubBtn = await page.$('button:has-text("GitHub"), a:has-text("GitHub")');
  if (githubBtn) {
    await githubBtn.click({ noWaitAfter: true }).catch(() => {});
    console.log('Clicked GitHub button');
  } else {
    console.log('GitHub button not found, trying alternative selectors...');
    const buttons = await page.$$eval('button, a', els => 
      els.map(e => ({ text: e.textContent.trim(), tag: e.tagName, cls: e.className }))
    );
    console.log('Available buttons:', JSON.stringify(buttons.slice(0, 10)));
  }

  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'r2-github-login.png' });
  console.log('Current URL:', page.url());

  // Step 3: Enter GitHub credentials
  const currentUrl = page.url();
  if (currentUrl.includes('github.com')) {
    console.log('Step 3: On GitHub login page, entering credentials...');
    
    // Check if we need to enter username/password
    const loginField = await page.$('#login_field, input[name="login"]');
    const passField = await page.$('#password, input[name="password"]');
    
    if (loginField && passField) {
      await loginField.fill('he2827987');
      await passField.fill('Heyang@42507002');
      await page.screenshot({ path: 'r3-credentials.png' });
      
      const signInBtn = await page.$('input[type="submit"], button[type="submit"]');
      if (signInBtn) {
        await signInBtn.click({ noWaitAfter: true }).catch(() => {});
        console.log('Clicked sign in button');
      }
      await new Promise(r => setTimeout(r, 8000));
      await page.screenshot({ path: 'r4-after-login.png' });
      console.log('After login URL:', page.url());
    }
    
    // Handle 2FA or authorization page if needed
    const pageText = await page.textContent('body').catch(() => '');
    if (pageText.includes('two-factor') || pageText.includes('2FA') || pageText.includes('authenticator')) {
      console.log('2FA required! Please complete it manually...');
    }
    
    if (pageText.includes('Authorize') || pageText.includes('authorize')) {
      console.log('Authorization page detected, clicking authorize...');
      const authBtn = await page.$('button:has-text("Authorize"), input[type="submit"]');
      if (authBtn) await authBtn.click();
      await new Promise(r => setTimeout(r, 5000));
    }
  }

  // Step 4: Wait for redirect to Render dashboard
  console.log('Step 4: Waiting for Render dashboard...');
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 3000));
    try {
      const url = page.url();
      if (url.includes('dashboard.render.com') && !url.includes('login')) {
        console.log('Dashboard reached:', url);
        break;
      }
    } catch (e) {}
  }

  await page.screenshot({ path: 'r5-dashboard.png' });
  console.log('Current URL:', page.url());

  // Step 5: Navigate to the deploy logs
  console.log('Step 5: Navigating to deploy logs...');
  const deployUrl = 'https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/deploys';
  await page.goto(deployUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'r6-deploys.png' });

  // Get all text from deploys page
  const deploysText = await page.textContent('body').catch(() => '');
  console.log('\n=== DEPLOYS PAGE TEXT (first 3000 chars) ===');
  console.log(deploysText.substring(0, 3000));

  // Click the most recent deploy to see its logs
  console.log('\nClicking on most recent deploy...');
  const firstDeploy = await page.$('a[href*="/deploys/dep-"]');
  if (firstDeploy) {
    await firstDeploy.click();
    await new Promise(r => setTimeout(r, 5000));
    await page.screenshot({ path: 'r7-deploy-detail.png' });

    const detailText = await page.textContent('body').catch(() => '');
    console.log('\n=== DEPLOY DETAIL TEXT ===');
    console.log(detailText.substring(0, 5000));

    // Try to get the log output specifically
    const logElements = await page.$$eval('[class*="log"], [class*="Log"], pre, code, [class*="terminal"], [class*="console"]', els =>
      els.map(e => e.textContent.substring(0, 5000))
    ).catch(() => []);
    if (logElements.length > 0) {
      console.log('\n=== LOG OUTPUT ===');
      logElements.forEach((log, i) => console.log(`Log ${i}:`, log));
    }
  } else {
    console.log('No deploy links found');
    // Try getting all links
    const allLinks = await page.$$eval('a', links => 
      links.map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 60) }))
        .filter(l => l.text.length > 0)
    ).catch(() => []);
    console.log('All links:', JSON.stringify(allLinks.slice(0, 20), null, 2));
  }

  console.log('\n=== Browser stays open. Press Ctrl+C to close. ===');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
