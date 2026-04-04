const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  console.log('🚀 启动 Render 自动部署诊断...\n');
  
  const browser = await chromium.launch({
    headless: false,
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  const diagnosisReport = {
    timestamp: new Date().toISOString(),
    serviceInfo: {},
    webhookInfo: {},
    recentDeploys: [],
    issues: [],
    solutions: []
  };

  try {
    // 步骤 1: 访问 Render Dashboard
    console.log('📍 步骤 1: 访问 Render Dashboard...');
    await page.goto('https://dashboard.render.com', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // 检查是否需要登录
    const currentUrl = page.url();
    if (currentUrl.includes('login') || currentUrl.includes('auth')) {
      console.log('⚠️  检测到登录页面，等待用户登录...');
      await page.waitForURL('**/dashboard.render.com/**', { timeout: 60000 });
      console.log('✅ 用户已登录');
    }
    
    await page.screenshot({ path: 'render-dashboard-home.png', fullPage: true });
    console.log('✅ 已访问 Render Dashboard\n');

    // 步骤 2: 查找 survey-product-backend 服务
    console.log('📍 步骤 2: 查找 survey-product-backend 服务...');
    
    // 尝试多种方式查找服务
    let serviceFound = false;
    
    // 方法 1: 通过搜索框
    try {
      const searchBox = await page.$('input[placeholder*="search" i], input[type="search"], input[aria-label*="search" i]');
      if (searchBox) {
        await searchBox.fill('survey-product-backend');
        await page.waitForTimeout(2000);
      }
    } catch (e) {
      console.log('搜索框未找到，继续其他方式...');
    }
    
    // 方法 2: 直接查找服务链接
    try {
      const serviceLink = await page.$('a[href*="survey-product-backend"], text=/survey-product-backend/i');
      if (serviceLink) {
        await serviceLink.click();
        serviceFound = true;
        console.log('✅ 找到并点击服务链接');
      }
    } catch (e) {
      console.log('服务链接未找到，尝试其他方式...');
    }
    
    // 方法 3: 查找所有服务卡片或列表项
    if (!serviceFound) {
      try {
        await page.waitForSelector('[class*="service"], [class*="Service"], a[href*="/srv-"]', { timeout: 5000 });
        const serviceElements = await page.$$('a[href*="/srv-"], [class*="service-name"], [class*="ServiceName"]');
        
        for (const element of serviceElements) {
          const text = await element.textContent();
          if (text && text.toLowerCase().includes('survey-product-backend')) {
            await element.click();
            serviceFound = true;
            console.log('✅ 通过列表找到服务');
            break;
          }
        }
      } catch (e) {
        console.log('服务列表未找到');
      }
    }
    
    if (!serviceFound) {
      console.log('⚠️  无法自动找到服务，请在浏览器中手动点击 survey-product-backend 服务');
      console.log('⏳ 等待 30 秒供你手动操作...');
      await page.waitForTimeout(30000);
    }
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'render-service-page.png', fullPage: true });
    console.log('✅ 已进入服务页面\n');

    // 步骤 3: 提取服务基本信息
    console.log('📍 步骤 3: 提取服务基本信息...');
    try {
      const pageInfo = await page.evaluate(() => {
        const bodyText = document.body.innerText;
        
        // 提取仓库信息
        let repository = '';
        const repoMatch = bodyText.match(/github\.com\/([^\s]+)/i);
        if (repoMatch) repository = repoMatch[0];
        
        // 提取分支信息
        let branch = '';
        const branchMatch = bodyText.match(/branch[:\s]+([^\s]+)/i);
        if (branchMatch) branch = branchMatch[1];
        
        // 检查是否有 Auto-Deploy 相关文本
        const hasAutoDeploy = bodyText.toLowerCase().includes('auto-deploy') || 
                             bodyText.toLowerCase().includes('auto deploy') ||
                             bodyText.toLowerCase().includes('deploy on push');
        
        // 提取服务状态
        let status = '';
        const statusMatch = bodyText.match(/(live|running|deploying|failed)/i);
        if (statusMatch) status = statusMatch[0];
        
        return {
          repository,
          branch,
          hasAutoDeploy,
          status,
          bodyText: bodyText.substring(0, 5000) // 保存前 5000 字符用于分析
        };
      });
      
      diagnosisReport.serviceInfo = pageInfo;
      console.log('  - 仓库:', pageInfo.repository || '未找到');
      console.log('  - 分支:', pageInfo.branch || '未找到');
      console.log('  - Auto-Deploy 提及:', pageInfo.hasAutoDeploy ? '是' : '否');
      console.log('  - 状态:', pageInfo.status || '未知');
    } catch (e) {
      console.log('⚠️  提取基本信息失败:', e.message);
    }
    console.log('');

    // 步骤 4: 进入 Settings 页面
    console.log('📍 步骤 4: 进入 Settings 页面...');
    try {
      // 尝试多种方式找到 Settings 链接
      const settingsSelectors = [
        'a:has-text("Settings")',
        'button:has-text("Settings")',
        '[href*="settings"]',
        'text=Settings',
        'nav a:has-text("Settings")'
      ];
      
      let settingsClicked = false;
      for (const selector of settingsSelectors) {
        try {
          const element = await page.$(selector);
          if (element) {
            await element.click();
            settingsClicked = true;
            console.log('✅ 点击 Settings 成功');
            break;
          }
        } catch (e) {
          continue;
        }
      }
      
      if (!settingsClicked) {
        console.log('⚠️  无法自动点击 Settings，请在浏览器中手动点击 Settings 标签');
        console.log('⏳ 等待 15 秒...');
        await page.waitForTimeout(15000);
      }
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'render-settings-page.png', fullPage: true });
      console.log('✅ 已进入 Settings 页面\n');
    } catch (e) {
      console.log('⚠️  进入 Settings 失败:', e.message, '\n');
    }

    // 步骤 5: 查找 Auto-Deploy 配置
    console.log('📍 步骤 5: 查找 Auto-Deploy 配置...');
    try {
      const autoDeployInfo = await page.evaluate(() => {
        const bodyText = document.body.innerText;
        const html = document.body.innerHTML;
        
        // 查找各种可能的 Auto-Deploy 元素
        const selectors = [
          'input[type="checkbox"][name*="auto" i]',
          'input[type="checkbox"][id*="auto" i]',
          'button[role="switch"][aria-label*="auto" i]',
          '[data-testid*="auto-deploy"]',
          '[class*="auto-deploy"]'
        ];
        
        let found = false;
        let enabled = false;
        let elementInfo = '';
        
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          if (element) {
            found = true;
            enabled = element.checked || element.getAttribute('aria-checked') === 'true';
            elementInfo = element.outerHTML.substring(0, 200);
            break;
          }
        }
        
        // 检查文本中是否包含相关内容
        const hasAutoDeployText = bodyText.toLowerCase().includes('auto deploy') ||
                                  bodyText.toLowerCase().includes('auto-deploy') ||
                                  bodyText.toLowerCase().includes('deploy on push');
        
        const hasWebhookText = bodyText.toLowerCase().includes('webhook') ||
                               bodyText.toLowerCase().includes('deploy hook');
        
        return {
          found,
          enabled,
          elementInfo,
          hasAutoDeployText,
          hasWebhookText,
          bodySnippet: bodyText.substring(0, 3000)
        };
      });
      
      diagnosisReport.autoDeployInfo = autoDeployInfo;
      
      console.log('  - 找到 Auto-Deploy 控件:', autoDeployInfo.found ? '是' : '否');
      console.log('  - Auto-Deploy 已启用:', autoDeployInfo.enabled ? '是' : '否');
      console.log('  - 页面包含 Auto-Deploy 文本:', autoDeployInfo.hasAutoDeployText ? '是' : '否');
      console.log('  - 页面包含 Webhook 文本:', autoDeployInfo.hasWebhookText ? '是' : '否');
      
      if (!autoDeployInfo.found && !autoDeployInfo.hasAutoDeployText) {
        diagnosisReport.issues.push('未找到 Auto-Deploy 配置选项');
        diagnosisReport.solutions.push('需要通过 Webhook 配置自动部署');
      } else if (autoDeployInfo.found && !autoDeployInfo.enabled) {
        diagnosisReport.issues.push('Auto-Deploy 未启用');
        diagnosisReport.solutions.push('启用 Auto-Deploy 选项');
      }
      
    } catch (e) {
      console.log('⚠️  检查 Auto-Deploy 失败:', e.message);
    }
    console.log('');

    // 步骤 6: 查找 Webhook/Deploy Hook
    console.log('📍 步骤 6: 查找 Webhook/Deploy Hook...');
    try {
      const webhookInfo = await page.evaluate(() => {
        const bodyText = document.body.innerText;
        const html = document.body.innerHTML;
        
        // 查找 webhook URL
        const urlPatterns = [
          /https:\/\/api\.render\.com\/deploy\/[^\s<]+/gi,
          /https:\/\/api\.render\.com\/hooks\/[^\s<]+/gi
        ];
        
        let webhookUrl = '';
        for (const pattern of urlPatterns) {
          const match = bodyText.match(pattern);
          if (match) {
            webhookUrl = match[0];
            break;
          }
        }
        
        // 查找 webhook 相关元素
        const webhookElements = [];
        const selectors = [
          '[class*="webhook"]',
          '[class*="deploy-hook"]',
          '[data-testid*="webhook"]',
          'code',
          'pre'
        ];
        
        for (const selector of selectors) {
          const elements = document.querySelectorAll(selector);
          elements.forEach(el => {
            const text = el.textContent || '';
            if (text.includes('render.com/deploy') || text.includes('render.com/hooks')) {
              webhookElements.push(text.substring(0, 200));
            }
          });
        }
        
        return {
          webhookUrl,
          webhookElements,
          hasWebhookSection: bodyText.toLowerCase().includes('webhook') || 
                             bodyText.toLowerCase().includes('deploy hook')
        };
      });
      
      diagnosisReport.webhookInfo = webhookInfo;
      
      console.log('  - Webhook URL:', webhookInfo.webhookUrl || '未找到');
      console.log('  - 找到 Webhook 元素:', webhookInfo.webhookElements.length);
      console.log('  - 包含 Webhook 部分:', webhookInfo.hasWebhookSection ? '是' : '否');
      
      if (!webhookInfo.webhookUrl && !webhookInfo.hasWebhookSection) {
        diagnosisReport.issues.push('未找到 Webhook 配置');
      }
      
    } catch (e) {
      console.log('⚠️  检查 Webhook 失败:', e.message);
    }
    console.log('');

    // 步骤 7: 检查部署历史
    console.log('📍 步骤 7: 检查部署历史...');
    try {
      // 尝试进入 Events 或 Deploys 页面
      const eventsSelectors = [
        'a:has-text("Events")',
        'a:has-text("Deploys")',
        'button:has-text("Events")',
        'text=Events',
        'nav a:has-text("Events")'
      ];
      
      let eventsClicked = false;
      for (const selector of eventsSelectors) {
        try {
          const element = await page.$(selector);
          if (element) {
            await element.click();
            eventsClicked = true;
            console.log('✅ 点击 Events/Deploys 成功');
            break;
          }
        } catch (e) {
          continue;
        }
      }
      
      if (eventsClicked) {
        await page.waitForTimeout(3000);
        await page.screenshot({ path: 'render-events-page.png', fullPage: true });
        
        const deployInfo = await page.evaluate(() => {
          const bodyText = document.body.innerText;
          
          // 查找最近的提交
          const commits = [];
          const commitPattern = /[a-f0-9]{7,}/gi;
          const matches = bodyText.match(commitPattern);
          if (matches) {
            commits.push(...matches.slice(0, 5));
          }
          
          // 检查是否有最新提交 cdd776a
          const hasLatestCommit = bodyText.toLowerCase().includes('cdd776a');
          
          return {
            recentCommits: commits,
            hasLatestCommit,
            bodySnippet: bodyText.substring(0, 2000)
          };
        });
        
        diagnosisReport.recentDeploys = deployInfo;
        
        console.log('  - 最近提交:', deployInfo.recentCommits.join(', '));
        console.log('  - 包含最新提交 cdd776a:', deployInfo.hasLatestCommit ? '是' : '否');
        
        if (!deployInfo.hasLatestCommit) {
          diagnosisReport.issues.push('最新提交 cdd776a 未触发部署');
        }
      } else {
        console.log('⚠️  无法进入 Events 页面');
      }
      
    } catch (e) {
      console.log('⚠️  检查部署历史失败:', e.message);
    }
    console.log('');

    // 步骤 8: 生成诊断报告
    console.log('📍 步骤 8: 生成诊断报告...\n');
    
    console.log('========================================');
    console.log('🔍 诊断报告');
    console.log('========================================\n');
    
    console.log('📋 服务信息:');
    console.log('  - 仓库:', diagnosisReport.serviceInfo.repository || '未找到');
    console.log('  - 分支:', diagnosisReport.serviceInfo.branch || '未找到');
    console.log('  - 状态:', diagnosisReport.serviceInfo.status || '未知');
    console.log('');
    
    console.log('🔧 配置状态:');
    console.log('  - Auto-Deploy:', diagnosisReport.autoDeployInfo?.enabled ? '✅ 已启用' : '❌ 未启用或未找到');
    console.log('  - Webhook:', diagnosisReport.webhookInfo?.webhookUrl ? '✅ 已配置' : '❌ 未找到');
    console.log('');
    
    console.log('⚠️  发现的问题:');
    if (diagnosisReport.issues.length === 0) {
      console.log('  - 未发现明显问题');
    } else {
      diagnosisReport.issues.forEach((issue, i) => {
        console.log(`  ${i + 1}. ${issue}`);
      });
    }
    console.log('');
    
    console.log('💡 建议的解决方案:');
    if (diagnosisReport.solutions.length === 0) {
      if (diagnosisReport.webhookInfo?.webhookUrl) {
        console.log('  1. Webhook URL 已找到，请在 GitHub 中添加 webhook');
        console.log('     URL:', diagnosisReport.webhookInfo.webhookUrl);
      } else {
        console.log('  1. 更新 render.yaml 并使用 Blueprint 重新部署');
        console.log('  2. 或者在 Render Dashboard 中手动配置 webhook');
      }
    } else {
      diagnosisReport.solutions.forEach((solution, i) => {
        console.log(`  ${i + 1}. ${solution}`);
      });
    }
    console.log('');
    
    // 保存报告到文件
    const reportPath = 'render-diagnosis-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(diagnosisReport, null, 2));
    console.log('📄 完整报告已保存到:', reportPath);
    console.log('');
    
    console.log('📸 截图已保存:');
    console.log('  - render-dashboard-home.png');
    console.log('  - render-service-page.png');
    console.log('  - render-settings-page.png');
    if (diagnosisReport.recentDeploys?.recentCommits) {
      console.log('  - render-events-page.png');
    }
    console.log('');
    
    console.log('⏳ 浏览器将保持打开 60 秒，你可以手动查看和操作...');
    console.log('   如果需要立即关闭，请按 Ctrl+C');
    
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('❌ 诊断过程出错:', error.message);
    console.error(error.stack);
    await page.screenshot({ path: 'render-error.png', fullPage: true });
  } finally {
    await browser.close();
    console.log('\n✅ 诊断完成，浏览器已关闭');
  }
})();
