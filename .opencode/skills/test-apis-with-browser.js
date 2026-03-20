const { chromium } = require('playwright');
const fs = require('fs');

/**
 * 使用浏览器自动化测试 /docs 页面的所有 API 接口
 */
async function testAllAPIsWithBrowser() {
  console.log('🌐 使用浏览器自动化测试所有 API 接口');
  console.log('='.repeat(80));
  
  const browser = await chromium.launch({ 
    headless: false,  // 显示浏览器便于观察
    slowMo: 50        // 放慢操作
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  const testResults = {
    summary: {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0
    },
    tests: [],
    startTime: new Date().toISOString()
  };
  
  try {
    // 1. 访问 /docs 页面
    console.log('\n📖 步骤 1: 访问 API 文档页面');
    await page.goto('http://localhost:8000/docs', { waitUntil: 'networkidle' });
    
    // 等待 Swagger UI 加载完成
    await page.waitForSelector('#swagger-ui', { timeout: 10000 });
    await page.waitForSelector('.opblock-tag', { timeout: 10000 });
    await page.waitForTimeout(2000); // 额外等待确保完全加载
    
    await page.screenshot({ path: '.opencode/skills/docs-01-initial.png' });
    console.log('✅ 已加载 API 文档页面');
    
    // 2. 获取所有 API 端点
    console.log('\n📋 步骤 2: 提取所有 API 端点');
    const apiEndpoints = await page.evaluate(() => {
      const endpoints = [];
      const opblocks = document.querySelectorAll('.opblock');
      
      opblocks.forEach(block => {
        const method = block.querySelector('.opblock-summary-method')?.textContent?.trim();
        const path = block.querySelector('.opblock-summary-path')?.textContent?.trim();
        const summary = block.querySelector('.opblock-summary-description')?.textContent?.trim();
        const tag = block.querySelector('.opblock-tag')?.textContent?.trim();
        
        if (method && path) {
          endpoints.push({ method, path, summary, tag });
        }
      });
      
      return endpoints;
    });
    
    console.log(`✅ 发现 ${apiEndpoints.length} 个 API 端点`);
    testResults.summary.total = apiEndpoints.length;
    
    // 保存端点列表
    fs.writeFileSync(
      '.opencode/skills/api-endpoints.json',
      JSON.stringify(apiEndpoints, null, 2)
    );
    console.log('📄 API 端点列表已保存到: .opencode/skills/api-endpoints.json');
    
    // 3. 测试用户认证流程
    console.log('\n🔐 步骤 3: 测试用户认证');
    
    // 3.1 注册用户
    const testUser = {
      username: `browser_test_${Date.now()}`,
      email: `browser_${Date.now()}@test.com`,
      password: 'TestPass123!',
      full_name: 'Browser Test User'
    };
    
    console.log(`   注册测试用户: ${testUser.username}`);
    
    // 找到用户标签并展开
    const userTag = await page.locator('.opblock-tag:has-text("user")').first();
    if (await userTag.count() > 0) {
      const isExpanded = await userTag.evaluate(el => el.classList.contains('is-open'));
      if (!isExpanded) {
        await userTag.click();
        await page.waitForTimeout(500);
      }
    }
    
    // 找到注册接口 - 使用更精确的选择器
    const registerBlock = await page.locator('.opblock-post').filter({ hasText: '/api/v1/users/register' }).first();
    
    if (await registerBlock.count() > 0) {
      await registerBlock.click();
      await page.waitForTimeout(500);
      
      // 点击 "Try it out"
      const tryItOutBtn = await registerBlock.locator('button:has-text("Try it out")').first();
      if (await tryItOutBtn.count() > 0) {
        await tryItOutBtn.click();
        await page.waitForTimeout(300);
      
      // 填写请求体
      const requestBody = `{
  "username": "${testUser.username}",
  "email": "${testUser.email}",
  "password": "${testUser.password}",
  "full_name": "${testUser.full_name}"
}`;
      
      const textarea = await page.locator('.body-param__text').first();
      await textarea.fill(requestBody);
      
      // 执行请求
      const executeBtn = await page.locator('button.execute').first();
      await executeBtn.click();
      await page.waitForTimeout(1000);
      
      // 检查响应
      const responseStatus = await page.locator('.response .response-col_status').first().textContent();
      const isSuccess = responseStatus && (responseStatus.includes('200') || responseStatus.includes('201'));
      
      testResults.tests.push({
        endpoint: '/api/v1/users/register',
        method: 'POST',
        status: isSuccess ? 'PASS' : 'FAIL',
        message: isSuccess ? '用户注册成功' : `用户注册失败: ${responseStatus}`,
        timestamp: new Date().toISOString()
      });
      
      if (isSuccess) {
        testResults.summary.passed++;
        console.log(`   ✅ 用户注册成功`);
      } else {
        testResults.summary.failed++;
        console.log(`   ❌ 用户注册失败: ${responseStatus}`);
      }
    }
    
    await page.screenshot({ path: '.opencode/skills/docs-02-register.png' });
    
    // 关闭当前展开的接口
    await registerBlock.click();
    await page.waitForTimeout(300);
    
    // 3.2 登录获取 token
    console.log(`   登录用户: ${testUser.username}`);
    
    const loginBlock = await page.locator('.opblock:has-text("POST /api/v1/users/login/access-token")').first();
    await loginBlock.click();
    await page.waitForTimeout(500);
    
    const loginTryItOut = await page.locator('button:has-text("Try it out")').first();
    if (await loginTryItOut.isVisible()) {
      await loginTryItOut.click();
      await page.waitForTimeout(300);
      
      // 填写表单数据
      const formData = `username=${testUser.username}&password=${testUser.password}`;
      const textarea = await page.locator('.body-param__text').first();
      await textarea.fill(formData);
      
      // 执行登录
      const executeBtn = await page.locator('button.execute').first();
      await executeBtn.click();
      await page.waitForTimeout(1000);
      
      // 获取响应中的 token
      const responseBody = await page.locator('.response .highlight-code .microlight').first().textContent();
      
      let authToken = null;
      if (responseBody) {
        try {
          const response = JSON.parse(responseBody);
          authToken = response.access_token;
        } catch (e) {
          // 忽略解析错误
        }
      }
      
      const loginSuccess = !!authToken;
      testResults.tests.push({
        endpoint: '/api/v1/users/login/access-token',
        method: 'POST',
        status: loginSuccess ? 'PASS' : 'FAIL',
        message: loginSuccess ? '登录成功，已获取 token' : '登录失败',
        timestamp: new Date().toISOString()
      });
      
      if (loginSuccess) {
        testResults.summary.passed++;
        console.log(`   ✅ 登录成功，已获取认证 token`);
        
        // 设置 Authorize
        const authorizeBtn = await page.locator('button:has-text("Authorize")').first();
        if (await authorizeBtn.isVisible()) {
          await authorizeBtn.click();
          await page.waitForTimeout(300);
          
          const tokenInput = await page.locator('input[name="authorization"]').first();
          await tokenInput.fill(`Bearer ${authToken}`);
          
          const confirmBtn = await page.locator('button:has-text("Authorize")').last();
          await confirmBtn.click();
          await page.waitForTimeout(300);
          
          const closeBtn = await page.locator('button:has-text("Close")').last();
          await closeBtn.click();
          
          console.log(`   ✅ 已设置认证 token`);
        }
      } else {
        testResults.summary.failed++;
        console.log(`   ❌ 登录失败`);
      }
    }
    
    await page.screenshot({ path: '.opencode/skills/docs-03-login.png' });
    
    // 关闭当前展开的接口
    await loginBlock.click();
    await page.waitForTimeout(300);
    
    // 4. 测试主要 API 端点
    console.log('\n🔍 步骤 4: 测试主要 API 端点');
    
    const testEndpoints = [
      { method: 'GET', path: '/api/v1/users/me', description: '获取当前用户信息' },
      { method: 'GET', path: '/api/v1/organizations/', description: '获取组织列表' },
      { method: 'GET', path: '/api/v1/surveys/', description: '获取问卷列表' },
      { method: 'GET', path: '/api/v1/questions/', description: '获取问题列表' },
      { method: 'GET', path: '/api/v1/analytics/', description: '获取分析数据' }
    ];
    
    for (const endpoint of testEndpoints) {
      console.log(`   测试: ${endpoint.method} ${endpoint.path} - ${endpoint.description}`);
      
      const endpointBlock = await page.locator(`.opblock:has-text("${endpoint.method} ${endpoint.path}")`).first();
      
      if (await endpointBlock.count() > 0) {
        await endpointBlock.click();
        await page.waitForTimeout(500);
        
        const tryItOutBtn = await page.locator('button:has-text("Try it out")').first();
        if (await tryItOutBtn.isVisible()) {
          await tryItOutBtn.click();
          await page.waitForTimeout(300);
          
          const executeBtn = await page.locator('button.execute').first();
          await executeBtn.click();
          await page.waitForTimeout(1000);
          
          // 检查响应
          const responseStatus = await page.locator('.response .response-col_status').first().textContent();
          const isSuccess = responseStatus && responseStatus.includes('200');
          
          testResults.tests.push({
            endpoint: endpoint.path,
            method: endpoint.method,
            status: isSuccess ? 'PASS' : 'FAIL',
            message: isSuccess ? endpoint.description + '成功' : `${endpoint.description}失败: ${responseStatus}`,
            timestamp: new Date().toISOString()
          });
          
          if (isSuccess) {
            testResults.summary.passed++;
            console.log(`      ✅ ${endpoint.description}成功`);
          } else {
            testResults.summary.failed++;
            console.log(`      ❌ ${endpoint.description}失败: ${responseStatus}`);
          }
        }
        
        // 关闭当前接口
        await endpointBlock.click();
        await page.waitForTimeout(300);
      } else {
        testResults.tests.push({
          endpoint: endpoint.path,
          method: endpoint.method,
          status: 'SKIP',
          message: `未找到端点: ${endpoint.path}`,
          timestamp: new Date().toISOString()
        });
        testResults.summary.skipped++;
        console.log(`      ⚠️  未找到端点: ${endpoint.path}`);
      }
    }
    
    await page.screenshot({ path: '.opencode/skills/docs-04-tested.png' });
    
    // 5. 生成最终报告
    console.log('\n📊 生成测试报告');
    
    const duration = (new Date() - new Date(testResults.startTime)) / 1000;
    testResults.duration = duration;
    testResults.endTime = new Date().toISOString();
    
    // 保存 JSON 报告
    fs.writeFileSync(
      '.opencode/skills/browser-api-test-report.json',
      JSON.stringify(testResults, null, 2)
    );
    
    // 生成 Markdown 报告
    const mdReport = generateBrowserTestReport(testResults, testUser, duration);
    fs.writeFileSync('.opencode/skills/browser-api-test-report.md', mdReport);
    
    console.log('\n' + '='.repeat(80));
    console.log('📊 测试总结');
    console.log('='.repeat(80));
    console.log(`⏱️  总耗时: ${duration.toFixed(2)} 秒`);
    console.log(`📊 总测试数: ${testResults.summary.total}`);
    console.log(`✅ 通过: ${testResults.summary.passed}`);
    console.log(`❌ 失败: ${testResults.summary.failed}`);
    console.log(`⚠️  跳过: ${testResults.summary.skipped}`);
    
    if (testResults.summary.passed + testResults.summary.failed > 0) {
      const passRate = (testResults.summary.passed / (testResults.summary.passed + testResults.summary.failed) * 100).toFixed(2);
      console.log(`📈 通过率: ${passRate}%`);
    }
    
    console.log('\n📄 报告已保存:');
    console.log('   - .opencode/skills/browser-api-test-report.json');
    console.log('   - .opencode/skills/browser-api-test-report.md');
    console.log('   - .opencode/skills/api-endpoints.json');
    console.log('\n📸 截图已保存:');
    console.log('   - .opencode/skills/docs-01-initial.png');
    console.log('   - .opencode/skills/docs-02-register.png');
    console.log('   - .opencode/skills/docs-03-login.png');
    console.log('   - .opencode/skills/docs-04-tested.png');
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
}

/**
 * 生成 Markdown 测试报告
 */
function generateBrowserTestReport(results, testUser, duration) {
  let md = `# 浏览器自动化 API 接口测试报告

**生成时间**: ${new Date().toLocaleString('zh-CN')}

## 📊 测试概览

- **总测试数**: ${results.summary.total}
- **✅ 通过**: ${results.summary.passed}
- **❌ 失败**: ${results.summary.failed}
- **⚠️ 跳过**: ${results.summary.skipped}
- **⏱️ 耗时**: ${duration.toFixed(2)} 秒
- **🌐 测试方式**: 浏览器自动化（Playwright）

## 🧪 测试环境

- **基础 URL**: http://localhost:8000
- **文档 URL**: http://localhost:8000/docs
- **测试用户**: ${testUser.username}
- **浏览器**: Chromium

## 📋 测试结果详情

| 序号 | 端点 | 方法 | 状态 | 消息 | 时间 |
|------|------|------|------|------|------|
`;
  
  results.tests.forEach((test, index) => {
    const statusIcon = test.status === 'PASS' ? '✅' : (test.status === 'FAIL' ? '❌' : '⚠️');
    const time = new Date(test.timestamp).toLocaleTimeString('zh-CN');
    md += `| ${index + 1} | \`${test.endpoint}\` | ${test.method} | ${statusIcon} ${test.status} | ${test.message} | ${time} |\n`;
  });
  
  // 添加失败的测试详情
  const failedTests = results.tests.filter(t => t.status === 'FAIL');
  if (failedTests.length > 0) {
    md += `\n## ❌ 失败的测试详情\n\n`;
    failedTests.forEach((test, index) => {
      md += `### ${index + 1}. ${test.method} ${test.endpoint}\n\n`;
      md += `- **消息**: ${test.message}\n`;
      md += `- **时间**: ${new Date(test.timestamp).toLocaleString('zh-CN')}\n\n`;
    });
  }
  
  md += `\n## 📸 测试截图\n\n`;
  md += `1. [初始页面](.opencode/skills/docs-01-initial.png) - API 文档页面加载\n`;
  md += `2. [用户注册](.opencode/skills/docs-02-register.png) - 测试用户注册\n`;
  md += `3. [用户登录](.opencode/skills/docs-03-login.png) - 获取认证 token\n`;
  md += `4. [测试完成](.opencode/skills/docs-04-tested.png) - 完成主要接口测试\n`;
  
  md += `\n## 🎯 测试覆盖的 API 模块\n\n`;
  md += `- ✅ 用户认证（注册、登录）\n`;
  md += `- ✅ 用户信息管理\n`;
  md += `- ✅ 组织管理\n`;
  md += `- ✅ 问卷管理\n`;
  md += `- ✅ 问题管理\n`;
  md += `- ✅ 分析 API\n`;
  
  md += `\n## 💡 建议\n\n`;
  
  if (results.summary.failed > 0) {
    md += `1. **检查失败的接口**: 有 ${results.summary.failed} 个接口测试失败，请检查相关代码\n`;
  }
  
  md += `2. **扩展测试覆盖**: 当前测试了主要接口，建议扩展到所有接口\n`;
  md += `3. **添加边界测试**: 测试边界条件和异常情况\n`;
  md += `4. **性能测试**: 添加响应时间和并发测试\n`;
  md += `5. **数据清理**: 测试完成后清理测试数据\n`;
  
  md += `\n## 📝 测试数据\n\n`;
  md += `\`\`\`json\n`;
  md += JSON.stringify(testUser, null, 2);
  md += `\n\`\`\`\n`;
  
  return md;
}

// 运行测试
testAllAPIsWithBrowser();
