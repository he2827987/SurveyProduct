const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    devtools: true // Open DevTools
  });
  
  const page = await browser.newPage();
  
  // Log all console messages
  page.on('console', msg => {
    console.log(`[${msg.type()}] ${msg.text()}`);
  });
  
  // Log all requests
  page.on('request', request => {
    if (request.url().includes('.js') || request.url().includes('.vue')) {
      console.log(`[REQUEST] ${request.method()} ${request.url()}`);
    }
  });
  
  // Log failed requests
  page.on('requestfailed', request => {
    console.log(`[FAILED] ${request.method()} ${request.url()} - ${request.failure().errorText}`);
  });
  
  // Log responses
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log(`[ERROR ${response.status()}] ${response.url()}`);
    }
  });
  
  console.log('Navigating to login page...\n');
  await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle2' });
  
  console.log('\n=== Waiting 10 seconds ===\n');
  await new Promise(r => setTimeout(r, 10000));
  
  // Check #app
  const appInfo = await page.evaluate(() => {
    const app = document.querySelector('#app');
    return {
      exists: !!app,
      innerHTML: app ? app.innerHTML : '',
      childCount: app ? app.children.length : 0
    };
  });
  
  console.log('\n=== #app Status ===');
  console.log('Exists:', appInfo.exists);
  console.log('Children:', appInfo.childCount);
  console.log('HTML length:', appInfo.innerHTML.length);
  
  await page.screenshot({ path: 'simple-test-screenshot.png' });
  
  console.log('\nBrowser will stay open for 30 seconds. Check DevTools for errors.');
  await new Promise(r => setTimeout(r, 30000));
  
  await browser.close();
})();
