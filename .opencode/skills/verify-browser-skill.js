const { chromium } = require('playwright');

/**
 * 浏览器自动化技能验证脚本
 * 用于验证 Playwright 和浏览器自动化技能是否正常工作
 */

(async () => {
  console.log('🚀 开始验证浏览器自动化技能...\n');
  
  let browser;
  try {
    // 1. 启动浏览器
    console.log('1️⃣  启动 Chromium 浏览器...');
    browser = await chromium.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    console.log('✅ 浏览器启动成功\n');
    
    // 2. 创建页面
    console.log('2️⃣  创建新页面...');
    const page = await browser.newPage();
    console.log('✅ 页面创建成功\n');
    
    // 3. 访问测试网站
    console.log('3️⃣  访问 example.com...');
    await page.goto('https://example.com', { waitUntil: 'networkidle' });
    console.log('✅ 页面加载完成\n');
    
    // 4. 获取页面标题
    console.log('4️⃣  获取页面信息...');
    const title = await page.title();
    const url = page.url();
    console.log(`   标题: ${title}`);
    console.log(`   URL: ${url}\n`);
    
    // 5. 截图测试
    console.log('5️⃣  测试截图功能...');
    const screenshotPath = '.opencode/skills/test-screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);
    
    // 6. 内容提取测试
    console.log('6️⃣  测试内容提取...');
    const heading = await page.textContent('h1');
    const paragraph = await page.textContent('p');
    console.log(`   H1: ${heading.substring(0, 50)}...`);
    console.log(`   P: ${paragraph.substring(0, 100)}...\n`);
    
    // 7. 元素交互测试
    console.log('7️⃣  测试元素定位...');
    const links = await page.$$('a');
    console.log(`✅ 找到 ${links.length} 个链接元素\n`);
    
    // 8. 性能测试
    console.log('8️⃣  测试页面加载性能...');
    const timing = await page.evaluate(() => {
      const perf = performance.timing;
      return {
        loadTime: perf.loadEventEnd - perf.navigationStart,
        domReady: perf.domContentLoadedEventEnd - perf.navigationStart,
        responseTime: perf.responseEnd - perf.requestStart
      };
    });
    console.log(`   页面加载时间: ${timing.loadTime}ms`);
    console.log(`   DOM Ready: ${timing.domReady}ms`);
    console.log(`   响应时间: ${timing.responseTime}ms\n`);
    
    // 成功总结
    console.log('='.repeat(50));
    console.log('✅ 所有测试通过！浏览器自动化技能工作正常');
    console.log('='.repeat(50));
    console.log('\n📦 已安装的技能:');
    console.log('   • browser-automation (LobeHub)');
    console.log('   • survey-browser-automation (自定义)');
    console.log('\n🎯 下一步:');
    console.log('   • 查看 .opencode/skills/BROWSER_AUTOMATION_QUICKSTART.md');
    console.log('   • 运行项目测试: npm run test:desktop');
    console.log('   • 在对话中提出自动化需求，我会自动使用这些技能');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.log('\n💡 可能的解决方案:');
    console.log('   1. 确保已安装依赖: npm install');
    console.log('   2. 安装浏览器: npx playwright install chromium');
    console.log('   3. 检查网络连接');
  } finally {
    if (browser) {
      await browser.close();
    }
  }
})();
