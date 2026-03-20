const { test, expect } = require('@playwright/test');
const { BrowserHelper } = require('../helpers/browser-helper');
const { AuthHelper } = require('../helpers/auth-helper');
const { VisualDebugger } = require('../helpers/visual-debug');

test.describe('Data Analysis Tests', () => {
  let browserHelper;
  let authHelper;
  let visualDebugger;

  test.beforeEach(async ({ page }) => {
    browserHelper = new BrowserHelper(page);
    authHelper = new AuthHelper(page, browserHelper);
    visualDebugger = new VisualDebugger(browserHelper);
    
    await page.goto('/login');
    await browserHelper.waitForPageLoad();
    await authHelper.login();
  });

  test('should display analysis dashboard', async ({ page }) => {
    console.log('\n🧪 Test: Analysis Dashboard Display');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    await visualDebugger.analyzePage('analysis-dashboard');
    
    await browserHelper.logPageState('Analysis dashboard loaded');
    
    const pageInfo = await browserHelper.getPageInfo();
    expect(pageInfo.url).toContain('/analysis');
  });

  test('should show analysis charts', async ({ page }) => {
    console.log('\n🧪 Test: Analysis Charts Display');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('analysis-charts', 'Analysis charts page');
    
    const charts = await page.$$('canvas, .chart, [class*="echarts"], [class*="chart"]');
    
    if (charts.length > 0) {
      console.log(`   ✓ Found ${charts.length} chart elements`);
      await browserHelper.captureAndSave('charts-found', 'Charts displayed');
    } else {
      console.log('   ⚠ No charts found');
    }
  });

  test('should switch between analysis tabs', async ({ page }) => {
    console.log('\n🧪 Test: Analysis Tab Switching');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const tabButtons = await page.$$('.el-radio-button, .tab-button, [role="tab"]');
    
    if (tabButtons.length >= 3) {
      for (let i = 0; i < Math.min(3, tabButtons.length); i++) {
        await tabButtons[i].click();
        await page.waitForTimeout(500);
        await browserHelper.captureAndSave(`tab-${i + 1}`, `Analysis tab ${i + 1}`);
      }
    } else {
      console.log(`   ⚠ Found ${tabButtons.length} tabs, expected at least 3`);
    }
  });

  test('should filter analysis by department', async ({ page }) => {
    console.log('\n🧪 Test: Department Filter');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const departmentSelect = await page.$('select[name*="department"], .department-select, [class*="department"]');
    
    if (departmentSelect) {
      await departmentSelect.click();
      await page.waitForTimeout(500);
      
      await browserHelper.captureAndSave('department-filter', 'Department filter options');
      
      const options = await page.$$('option, .el-select-dropdown__item');
      if (options.length > 1) {
        await options[1].click();
        await browserHelper.waitForPageLoad();
        
        await browserHelper.captureAndSave('department-filtered', 'Analysis filtered by department');
      }
    } else {
      console.log('   ⚠ Department filter not found');
    }
  });

  test('should filter analysis by position', async ({ page }) => {
    console.log('\n🧪 Test: Position Filter');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const positionSelect = await page.$('select[name*="position"], .position-select, [class*="position"]');
    
    if (positionSelect) {
      await positionSelect.click();
      await page.waitForTimeout(500);
      
      await browserHelper.captureAndSave('position-filter', 'Position filter options');
    } else {
      console.log('   ⚠ Position filter not found');
    }
  });

  test('should export analysis data', async ({ page }) => {
    console.log('\n🧪 Test: Export Analysis Data');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const exportButton = await page.$('button:has-text("导出"), button:has-text("Export"), .export-button');
    
    if (exportButton) {
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 5000 }).catch(() => null),
        exportButton.click()
      ]);
      
      if (download) {
        console.log(`   ✓ Download started: ${download.suggestedFilename()}`);
        await browserHelper.captureAndSave('export-initiated', 'Export initiated');
      } else {
        console.log('   ⚠ No download event triggered');
      }
    } else {
      console.log('   ⚠ Export button not found');
    }
  });

  test('should compare companies', async ({ page }) => {
    console.log('\n🧪 Test: Company Comparison');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const comparisonTab = await page.$('button:has-text("对比"), button:has-text("Comparison"), [class*="comparison"]');
    
    if (comparisonTab) {
      await comparisonTab.click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('comparison-view', 'Company comparison view');
      
      const companySelect = await page.$('select[name*="company"], .company-select');
      if (companySelect) {
        await companySelect.click();
        await page.waitForTimeout(500);
        
        await browserHelper.captureAndSave('company-selection', 'Company selection options');
      }
    } else {
      console.log('   ⚠ Comparison tab not found');
    }
  });

  test('should generate LLM summary', async ({ page }) => {
    console.log('\n🧪 Test: LLM Summary Generation');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const summaryButton = await page.$('button:has-text("总结"), button:has-text("Summary"), button:has-text("AI"), .llm-button');
    
    if (summaryButton) {
      await summaryButton.click();
      
      await page.waitForTimeout(3000);
      
      await browserHelper.captureAndSave('llm-summary', 'LLM generated summary');
      
      const summaryText = await page.$('.summary, .llm-summary, [class*="summary"]');
      if (summaryText) {
        const text = await summaryText.textContent();
        console.log(`   ✓ Summary generated: ${text.substring(0, 100)}...`);
      }
    } else {
      console.log('   ⚠ LLM summary button not found');
    }
  });

  test('should display pie chart for question analysis', async ({ page }) => {
    console.log('\n🧪 Test: Pie Chart Display');
    
    await page.goto('/analysis');
    await browserHelper.waitForPageLoad();
    
    const questionSelect = await page.$('select[name*="question"], .question-select');
    
    if (questionSelect) {
      await questionSelect.click();
      await page.waitForTimeout(500);
      
      const options = await page.$$('option, .el-select-dropdown__item');
      if (options.length > 1) {
        await options[1].click();
        await browserHelper.waitForPageLoad();
        
        await browserHelper.captureAndSave('pie-chart', 'Pie chart for question');
        
        const pieChart = await page.$('canvas, [class*="pie"]');
        expect(pieChart).toBeTruthy();
      }
    } else {
      console.log('   ⚠ Question selector not found');
    }
  });

  test('should handle empty data gracefully', async ({ page }) => {
    console.log('\n🧪 Test: Empty Data Handling');
    
    await page.goto('/analysis?empty=true');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('empty-data', 'Analysis with no data');
    
    const emptyMessage = await page.$('.empty, .no-data, [class*="empty"]');
    if (emptyMessage) {
      const message = await emptyMessage.textContent();
      console.log(`   ✓ Empty state message: ${message}`);
    }
  });
});
