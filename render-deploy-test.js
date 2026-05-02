const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'en-US'
  });
  const page = await context.newPage();

  console.log('Opening Render login page...');
  await page.goto('https://dashboard.render.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.screenshot({ path: 'render-step1-login.png', fullPage: true });
  console.log('Screenshot saved: render-step1-login.png');
  console.log('Current URL:', page.url());

  console.log('\n=== Please login to Render manually ===');
  console.log('Waiting for you to complete login...\n');

  // Wait for navigation away from login page
  try {
    await page.waitForURL(url => {
      const u = url.toString();
      return u.includes('dashboard.render.com') && !u.includes('login');
    }, { timeout: 300000 }); // 5 minutes
  } catch (e) {
    console.log('Timeout or navigation error, continuing...');
  }

  // Wait for page to stabilize after login
  await new Promise(r => setTimeout(r, 3000));

  try {
    const currentUrl = page.url();
    console.log('After login URL:', currentUrl);
    await page.screenshot({ path: 'render-step2-after-login.png', fullPage: true });
    console.log('After-login screenshot saved');
  } catch (e) {
    console.log('Error getting URL after login:', e.message);
  }

  // Now navigate to dashboard
  console.log('\nNavigating to dashboard...');
  try {
    await page.goto('https://dashboard.render.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: 'render-step3-dashboard.png', fullPage: true });
    console.log('Dashboard screenshot saved');
    
    const dashText = await page.textContent('body').catch(() => '');
    console.log('Dashboard content snippet:', dashText.substring(0, 500));
    
    // Find all links on the page
    const allLinks = await page.$$eval('a', links => 
      links.map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 80) }))
        .filter(l => l.text.length > 0 && !l.href.includes('#') && !l.href.includes('mailto'))
    ).catch(() => []);
    console.log('\nAll links on dashboard:', JSON.stringify(allLinks.slice(0, 20), null, 2));

    // Check for survey-related services
    const surveyEls = await page.$$eval('*', els => 
      els.filter(e => e.textContent.toLowerCase().includes('survey') && e.children.length < 3)
        .map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 100) }))
        .slice(0, 10)
    ).catch(() => []);
    console.log('\nSurvey-related elements:', JSON.stringify(surveyEls, null, 2));

  } catch (e) {
    console.log('Error on dashboard:', e.message);
  }

  // Try the Blueprint/repo selection page
  console.log('\nTrying blueprint creation page...');
  try {
    await page.goto('https://dashboard.render.com/select-repo?type=blueprint', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: 'render-step4-blueprint.png', fullPage: true });
    console.log('Blueprint page screenshot saved');
    
    const bpText = await page.textContent('body').catch(() => '');
    console.log('Blueprint page snippet:', bpText.substring(0, 800));

    // Find clickable elements related to SurveyProduct
    const repoEls = await page.$$eval('a, button, [role="button"], [class*="repo"]', els =>
      els.filter(e => e.textContent.toLowerCase().includes('survey') || e.textContent.toLowerCase().includes('product'))
        .map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 100), href: e.href || '', cls: e.className.substring(0, 60) }))
    ).catch(() => []);
    console.log('\nSurvey/Product repo elements:', JSON.stringify(repoEls, null, 2));

    // If we can find and click the SurveyProduct repo, do it
    const surveyRepoLink = await page.$('text=SurveyProduct');
    if (surveyRepoLink) {
      console.log('\nFound SurveyProduct repo link! Clicking it...');
      await surveyRepoLink.click();
      await new Promise(r => setTimeout(r, 3000));
      await page.screenshot({ path: 'render-step5-surveyproduct.png', fullPage: true });
      console.log('SurveyProduct page screenshot saved');
      
      const spText = await page.textContent('body').catch(() => '');
      console.log('SurveyProduct page snippet:', spText.substring(0, 1000));
    } else {
      console.log('SurveyProduct repo not found on blueprint page');
      
      // Look for any repo listing
      const allRepoEls = await page.$$eval('[class*="repo"], [class*="Repo"], [class*="repository"]', els =>
        els.map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 100), cls: e.className.substring(0, 60) }))
          .slice(0, 15)
      ).catch(() => []);
      console.log('Repository elements:', JSON.stringify(allRepoEls, null, 2));
    }
  } catch (e) {
    console.log('Error on blueprint page:', e.message);
  }

  // Also check if there's an existing service we can look at
  console.log('\nChecking for existing web services...');
  try {
    await page.goto('https://dashboard.render.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await new Promise(r => setTimeout(r, 2000));

    // Look for "New +" or "Create" button
    const newButtons = await page.$$eval('button, a', els =>
      els.filter(e => /new|create|add|deploy/i.test(e.textContent))
        .map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 50), href: e.href || '' }))
    ).catch(() => []);
    console.log('New/Create buttons:', JSON.stringify(newButtons, null, 2));

    // Check for any existing services listed
    const servicesList = await page.$$eval('[class*="service"], [class*="Service"], [data-testid*="service"]', els =>
      els.map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 100), cls: e.className.substring(0, 80) }))
        .slice(0, 10)
    ).catch(() => []);
    console.log('Service elements:', JSON.stringify(servicesList, null, 2));

    await page.screenshot({ path: 'render-step6-final.png', fullPage: true });
    console.log('Final screenshot saved');
  } catch (e) {
    console.log('Error checking existing services:', e.message);
  }

  console.log('\n=== Browser is open for manual inspection ===');
  console.log('Press Ctrl+C to close when done.');
  await new Promise(() => {});
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
