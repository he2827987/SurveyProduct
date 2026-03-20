const { test, expect } = require('@playwright/test');
const { BrowserHelper } = require('../helpers/browser-helper');
const { AuthHelper } = require('../helpers/auth-helper');
const { VisualDebugger } = require('../helpers/visual-debug');

test.describe('Survey Management Tests', () => {
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

  test('should display survey list page', async ({ page }) => {
    console.log('\n🧪 Test: Survey List Display');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    await visualDebugger.analyzePage('survey-list');
    
    await browserHelper.logPageState('Survey list page loaded');
    
    const pageInfo = await browserHelper.getPageInfo();
    expect(pageInfo.url).toContain('/surveys');
  });

  test('should create a new survey', async ({ page }) => {
    console.log('\n🧪 Test: Create New Survey');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('survey-list-before-create', 'Survey list before creating new');
    
    const createButton = await page.$('button:has-text("新建"), button:has-text("创建"), button:has-text("Create")');
    
    if (createButton) {
      await createButton.click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('survey-create-form', 'Survey creation form');
      
      const titleInput = await page.$('input[placeholder*="标题"], input[placeholder*="title"], input[name="title"]');
      if (titleInput) {
        await titleInput.fill('自动化测试问卷 - ' + Date.now());
        
        const descInput = await page.$('textarea[placeholder*="描述"], textarea[placeholder*="description"]');
        if (descInput) {
          await descInput.fill('这是一个自动化测试创建的问卷');
        }
        
        await browserHelper.captureAndSave('survey-form-filled', 'Survey form filled');
        
        const submitButton = await page.$('button:has-text("提交"), button:has-text("保存"), button[type="submit"]');
        if (submitButton) {
          await submitButton.click();
          await browserHelper.waitForPageLoad();
          
          await browserHelper.captureAndSave('survey-created', 'Survey created successfully');
        }
      }
    } else {
      console.log('   ⚠ Create button not found, checking page structure');
      await visualDebugger.analyzePage('no-create-button');
    }
  });

  test('should view survey details', async ({ page }) => {
    console.log('\n🧪 Test: View Survey Details');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    const surveyItems = await page.$$('.survey-item, .survey-card, [class*="survey"]');
    
    if (surveyItems.length > 0) {
      await surveyItems[0].click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('survey-details', 'Survey detail page');
      
      const pageInfo = await browserHelper.getPageInfo();
      await browserHelper.logPageState('Survey details loaded');
    } else {
      console.log('   ⚠ No surveys found to view');
      await browserHelper.captureAndSave('no-surveys', 'No surveys available');
    }
  });

  test('should edit existing survey', async ({ page }) => {
    console.log('\n🧪 Test: Edit Survey');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    const editButton = await page.$('button:has-text("编辑"), button:has-text("Edit"), .edit-button');
    
    if (editButton) {
      await editButton.click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('survey-edit-form', 'Survey edit form');
      
      const titleInput = await page.$('input[placeholder*="标题"], input[placeholder*="title"], input[name="title"]');
      if (titleInput) {
        const currentValue = await titleInput.inputValue();
        await titleInput.fill(currentValue + ' - 已编辑');
        
        await browserHelper.captureAndSave('survey-edited', 'Survey form after editing');
      }
    } else {
      console.log('   ⚠ Edit button not found');
    }
  });

  test('should delete survey', async ({ page }) => {
    console.log('\n🧪 Test: Delete Survey');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    await browserHelper.captureAndSave('before-delete', 'Survey list before deletion');
    
    const deleteButton = await page.$('button:has-text("删除"), button:has-text("Delete"), .delete-button');
    
    if (deleteButton) {
      page.on('dialog', async dialog => {
        await dialog.accept();
      });
      
      await deleteButton.click();
      await page.waitForTimeout(1000);
      
      await browserHelper.captureAndSave('after-delete', 'Survey list after deletion');
    } else {
      console.log('   ⚠ Delete button not found');
    }
  });

  test('should generate QR code for survey', async ({ page }) => {
    console.log('\n🧪 Test: Generate QR Code');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    const qrButton = await page.$('button:has-text("二维码"), button:has-text("QR"), .qr-button');
    
    if (qrButton) {
      await qrButton.click();
      await page.waitForTimeout(1000);
      
      await browserHelper.captureAndSave('qr-code', 'QR code generated');
      
      const qrImage = await page.$('img[src*="qr"], canvas, .qr-code');
      expect(qrImage).toBeTruthy();
    } else {
      console.log('   ⚠ QR code button not found');
    }
  });

  test('should navigate survey pages', async ({ page }) => {
    console.log('\n🧪 Test: Survey Navigation');
    
    await page.goto('/surveys');
    await browserHelper.waitForPageLoad();
    
    const paginationButtons = await page.$$('.pagination button, .page-button');
    
    if (paginationButtons.length > 0) {
      await paginationButtons[1].click();
      await browserHelper.waitForPageLoad();
      
      await browserHelper.captureAndSave('survey-page-2', 'Survey list page 2');
    } else {
      console.log('   ⚠ No pagination found');
    }
  });
});
