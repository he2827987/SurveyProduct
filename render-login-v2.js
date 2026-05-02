const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  page.on('console', msg => console.log('BROWSER:', msg.text()));

  console.log('Opening Render login...');
  await page.goto('https://dashboard.render.com/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await new Promise(r => setTimeout(r, 3000));
  
  // Try Render email/password login instead of GitHub OAuth
  // The user's GitHub email is he2827987@gmail.com - might be same for Render
  console.log('Looking for email/password login fields...');
  
  const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="Email"]');
  const passInput = await page.$('input[type="password"]');
  
  if (emailInput && passInput) {
    console.log('Found email/password fields');
    await emailInput.fill('he2827987@gmail.com');
    await passInput.fill('Heyang@42507002');
    await page.screenshot({ path: 'rl-1-filled.png' });
    
    const submitBtn = await page.$('button[type="submit"], button:has-text("Sign in")');
    if (submitBtn) {
      await submitBtn.click({ noWaitAfter: true }).catch(() => {});
      console.log('Clicked submit');
    }
  } else {
    console.log('Email/password fields not found, trying GitHub OAuth flow...');
    await page.screenshot({ path: 'rl-1-nofields.png' });
    
    // Try GitHub OAuth - use page.locator for better matching
    const ghBtn = page.locator('button:has-text("GitHub")').first();
    if (await ghBtn.isVisible().catch(() => false)) {
      console.log('Found GitHub button via locator');
      
      // Listen for new tab/popup
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 15000 }).catch(() => null),
        ghBtn.click()
      ]);
      
      const ghPage = popup || page;
      await new Promise(r => setTimeout(r, 5000));
      console.log('GitHub page URL:', ghPage.url());
      await ghPage.screenshot({ path: 'rl-2-github.png' });
      
      // Enter GitHub credentials
      const ghLogin = await ghPage.$('#login_field, input[name="login"]');
      const ghPass = await ghPage.$('#password, input[name="password"]');
      
      if (ghLogin && ghPass) {
        await ghLogin.fill('he2827987');
        await ghPass.fill('Heyang@42507002');
        
        const ghSubmit = await ghPage.$('input[type="submit"]');
        if (ghSubmit) {
          await ghSubmit.click({ noWaitAfter: true }).catch(() => {});
          console.log('GitHub credentials submitted');
        }
      } else {
        const ghText = await ghPage.textContent('body').catch(() => '');
        console.log('GitHub page text:', ghText.substring(0, 500));
      }
    }
  }

  // Wait for login to complete
  console.log('Waiting for login to complete...');
  for (let i = 0; i < 40; i++) {
    await new Promise(r => setTimeout(r, 3000));
    try {
      const url = page.url();
      if (url.includes('dashboard.render.com') && !url.includes('login') && !url.includes('sign')) {
        console.log('Login successful! URL:', url);
        break;
      }
      // Check popup pages too
      for (const p of context.pages()) {
        const pUrl = p.url();
        if (pUrl.includes('dashboard.render.com') && !pUrl.includes('login')) {
          console.log('Login detected on popup page:', pUrl);
          break;
        }
      }
    } catch (e) {}
  }
  
  await page.screenshot({ path: 'rl-3-after-login.png' });
  console.log('Current URL:', page.url());

  // Check all open pages
  for (const p of context.pages()) {
    console.log('Open page:', p.url());
  }

  // Navigate to deploys
  console.log('\nNavigating to deploys...');
  await page.goto('https://dashboard.render.com/web/srv-d379sp8gjchc73c3ju9g/deploys', { 
    waitUntil: 'domcontentloaded', timeout: 60000 
  });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: 'rl-4-deploys.png' });
  
  const text = await page.textContent('body').catch(() => '');
  console.log('Deploys page text:', text.substring(0, 3000));

  // Click latest deploy
  const deployLink = await page.$('a[href*="/deploys/dep-"]');
  if (deployLink) {
    await deployLink.click({ noWaitAfter: true }).catch(() => {});
    await new Promise(r => setTimeout(r, 5000));
    await page.screenshot({ path: 'rl-5-deploy-detail.png' });
    
    const detail = await page.textContent('body').catch(() => '');
    console.log('\n=== DEPLOY DETAIL ===');
    console.log(detail.substring(0, 5000));

    // Look for expandable log sections
    const logBtns = await page.$$eval('button, [role="button"]', els =>
      els.filter(e => /log|show|expand|view|detail/i.test(e.textContent))
        .map(e => ({ text: e.textContent.trim().substring(0, 60), cls: e.className.substring(0, 40) }))
    ).catch(() => []);
    console.log('\nLog-related buttons:', JSON.stringify(logBtns, null, 2));

    // Try to get pre/code/terminal content
    const logContent = await page.$$eval('pre, code, [class*="log"], [class*="terminal"], [class*="console"], [class*="output"]', els =>
      els.map(e => ({ cls: e.className.substring(0, 40), text: e.textContent.substring(0, 3000) }))
    ).catch(() => []);
    if (logContent.length > 0) {
      console.log('\n=== LOG CONTENT ===');
      logContent.forEach((l, i) => {
        console.log(`\n--- ${l.cls} ---`);
        console.log(l.text);
      });
    }
  }

  console.log('\nBrowser stays open. Ctrl+C to close.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
