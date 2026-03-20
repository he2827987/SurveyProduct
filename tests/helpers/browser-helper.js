const fs = require('fs').promises;
const path = require('path');

class BrowserHelper {
  constructor(page, testInfo = null) {
    this.page = page;
    this.testInfo = testInfo;
    this.screenshotDir = path.join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct');
    this.stepCounter = 0;
  }

  async ensureScreenshotDir() {
    try {
      await fs.mkdir(this.screenshotDir, { recursive: true });
    } catch (error) {
      console.error('Failed to create screenshot directory:', error.message);
    }
  }

  async captureAndSave(stepName, description = '') {
    await this.ensureScreenshotDir();
    this.stepCounter++;
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${String(this.stepCounter).padStart(2, '0')}_${stepName}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);
    
    await this.page.screenshot({
      path: filepath,
      fullPage: true
    });
    
    console.log(`📸 Screenshot saved: ${filename}`);
    if (description) {
      console.log(`   Description: ${description}`);
    }
    
    return {
      path: filepath,
      filename: filename,
      stepName: stepName,
      description: description,
      url: this.page.url()
    };
  }

  async getPageInfo() {
    return await this.page.evaluate(() => {
      const getVisibleText = (element) => {
        if (element.offsetParent === null) return '';
        return element.innerText || '';
      };
      
      return {
        title: document.title,
        url: window.location.href,
        buttons: Array.from(document.querySelectorAll('button')).slice(0, 20).map(b => ({
          text: b.textContent.trim(),
          visible: b.offsetParent !== null,
          disabled: b.disabled
        })),
        links: Array.from(document.querySelectorAll('a')).slice(0, 20).map(a => ({
          text: a.textContent.trim(),
          href: a.href,
          visible: a.offsetParent !== null
        })),
        inputs: Array.from(document.querySelectorAll('input, textarea, select')).slice(0, 20).map(i => ({
          type: i.type || i.tagName.toLowerCase(),
          name: i.name || i.id || i.placeholder,
          placeholder: i.placeholder,
          visible: i.offsetParent !== null,
          required: i.required
        })),
        forms: Array.from(document.querySelectorAll('form')).length,
        alerts: Array.from(document.querySelectorAll('.el-message, .alert, [role="alert"]')).map(a => a.textContent.trim())
      };
    });
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle', { timeout: 30000 });
    await this.page.waitForTimeout(500);
  }

  async clickElement(selector, options = {}) {
    try {
      await this.page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
      await this.page.click(selector, options);
      await this.waitForPageLoad();
      return true;
    } catch (error) {
      console.error(`Failed to click element ${selector}:`, error.message);
      return false;
    }
  }

  async fillInput(selector, value) {
    try {
      await this.page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
      await this.page.fill(selector, value);
      return true;
    } catch (error) {
      console.error(`Failed to fill input ${selector}:`, error.message);
      return false;
    }
  }

  async selectOption(selector, value) {
    try {
      await this.page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
      await this.page.selectOption(selector, value);
      return true;
    } catch (error) {
      console.error(`Failed to select option ${selector}:`, error.message);
      return false;
    }
  }

  async isElementVisible(selector) {
    try {
      const element = await this.page.$(selector);
      if (!element) return false;
      return await element.isVisible();
    } catch (error) {
      return false;
    }
  }

  async getElementText(selector) {
    try {
      await this.page.waitForSelector(selector, { timeout: 5000 });
      return await this.page.textContent(selector);
    } catch (error) {
      return null;
    }
  }

  async scrollDown(pixels = 500) {
    await this.page.evaluate((scrollPixels) => {
      window.scrollBy(0, scrollPixels);
    }, pixels);
    await this.page.waitForTimeout(500);
  }

  async scrollUp(pixels = 500) {
    await this.page.evaluate((scrollPixels) => {
      window.scrollBy(0, -scrollPixels);
    }, pixels);
    await this.page.waitForTimeout(500);
  }

  async scrollToBottom() {
    await this.page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await this.page.waitForTimeout(1000);
  }

  async scrollToTop() {
    await this.page.evaluate(() => {
      window.scrollTo(0, 0);
    });
    await this.page.waitForTimeout(500);
  }

  async handleDialog(accept = true, promptText = '') {
    this.page.on('dialog', async dialog => {
      if (promptText && dialog.type() === 'prompt') {
        await dialog.accept(promptText);
      } else if (accept) {
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    });
  }

  async getNetworkRequests() {
    const requests = [];
    this.page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });
    return requests;
  }

  async waitForAPIResponse(urlPattern, timeout = 10000) {
    try {
      const response = await this.page.waitForResponse(
        response => response.url().includes(urlPattern),
        { timeout }
      );
      return response;
    } catch (error) {
      console.error(`Failed to wait for API response ${urlPattern}:`, error.message);
      return null;
    }
  }

  async takeFullPageScreenshot(filename) {
    await this.ensureScreenshotDir();
    const filepath = path.join(this.screenshotDir, filename);
    await this.page.screenshot({
      path: filepath,
      fullPage: true
    });
    return filepath;
  }

  async getElementScreenshot(selector, filename) {
    await this.ensureScreenshotDir();
    const filepath = path.join(this.screenshotDir, filename);
    const element = await this.page.$(selector);
    if (element) {
      await element.screenshot({ path: filepath });
      return filepath;
    }
    return null;
  }

  async logPageState(context = '') {
    const info = await this.getPageInfo();
    console.log('\n=== Page State ===');
    if (context) console.log(`Context: ${context}`);
    console.log(`URL: ${info.url}`);
    console.log(`Title: ${info.title}`);
    console.log(`Visible Buttons: ${info.buttons.filter(b => b.visible).length}`);
    console.log(`Visible Links: ${info.links.filter(l => l.visible).length}`);
    console.log(`Visible Inputs: ${info.inputs.filter(i => i.visible).length}`);
    if (info.alerts.length > 0) {
      console.log(`Alerts: ${info.alerts.join(', ')}`);
    }
    console.log('==================\n');
  }
}

module.exports = { BrowserHelper };
