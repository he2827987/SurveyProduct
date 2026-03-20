const fs = require('fs').promises;
const path = require('path');

class VisualDebugger {
  constructor(browserHelper) {
    this.browserHelper = browserHelper;
    this.page = browserHelper.page;
    this.debugLog = [];
  }

  async analyzePage(pageName) {
    console.log(`\n🔍 Analyzing page: ${pageName}`);
    
    const screenshot = await this.browserHelper.captureAndSave(
      `analyze-${pageName}`,
      `Visual analysis of ${pageName}`
    );
    
    const pageInfo = await this.browserHelper.getPageInfo();
    
    const analysis = {
      timestamp: new Date().toISOString(),
      pageName: pageName,
      screenshot: screenshot,
      pageInfo: pageInfo,
      recommendations: []
    };
    
    if (pageInfo.buttons.filter(b => b.visible).length === 0) {
      analysis.recommendations.push('No visible buttons found on this page');
    }
    
    if (pageInfo.alerts.length > 0) {
      analysis.recommendations.push(`Alerts detected: ${pageInfo.alerts.join(', ')}`);
    }
    
    this.debugLog.push(analysis);
    
    await this.logAnalysis(analysis);
    
    return analysis;
  }

  async logAnalysis(analysis) {
    console.log('\n=== Page Analysis ===');
    console.log(`Page: ${analysis.pageName}`);
    console.log(`URL: ${analysis.pageInfo.url}`);
    console.log(`Title: ${analysis.pageInfo.title}`);
    console.log(`Visible Buttons: ${analysis.pageInfo.buttons.filter(b => b.visible).length}`);
    console.log(`Visible Links: ${analysis.pageInfo.links.filter(l => l.visible).length}`);
    console.log(`Forms: ${analysis.pageInfo.forms}`);
    
    if (analysis.pageInfo.alerts.length > 0) {
      console.log('Alerts:', analysis.pageInfo.alerts);
    }
    
    if (analysis.recommendations.length > 0) {
      console.log('\nRecommendations:');
      analysis.recommendations.forEach((rec, i) => {
        console.log(`  ${i + 1}. ${rec}`);
      });
    }
    console.log('====================\n');
  }

  async checkElementVisibility(selector, elementName) {
    const isVisible = await this.browserHelper.isElementVisible(selector);
    const status = isVisible ? '✅' : '❌';
    console.log(`${status} ${elementName}: ${isVisible ? 'Visible' : 'Not visible'}`);
    return isVisible;
  }

  async compareScreenshots(beforePath, afterPath, description) {
    console.log(`\n📸 Comparing screenshots: ${description}`);
    console.log(`   Before: ${path.basename(beforePath)}`);
    console.log(`   After: ${path.basename(afterPath)}`);
    
    return {
      before: beforePath,
      after: afterPath,
      description: description
    };
  }

  async debugForm(formSelector, formName) {
    console.log(`\n🔍 Debugging form: ${formName}`);
    
    const form = await this.page.$(formSelector);
    if (!form) {
      console.log(`   ❌ Form not found: ${formSelector}`);
      return null;
    }
    
    const formData = await this.page.evaluate((selector) => {
      const form = document.querySelector(selector);
      const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
      
      return inputs.map(input => ({
        type: input.type || input.tagName.toLowerCase(),
        name: input.name || input.id,
        placeholder: input.placeholder,
        value: input.value,
        required: input.required,
        visible: input.offsetParent !== null
      }));
    }, formSelector);
    
    console.log(`   Found ${formData.length} input fields:`);
    formData.forEach((field, i) => {
      console.log(`     ${i + 1}. ${field.name || field.placeholder || 'unnamed'} (${field.type}) - ${field.visible ? 'visible' : 'hidden'}`);
    });
    
    await this.browserHelper.captureAndSave(`form-${formName}`, `Form debug: ${formName}`);
    
    return formData;
  }

  async debugNavigation(fromUrl, toUrl, linkSelector) {
    console.log(`\n🧭 Debugging navigation from ${fromUrl} to ${toUrl}`);
    
    await this.page.goto(fromUrl);
    await this.browserHelper.waitForPageLoad();
    await this.browserHelper.captureAndSave('nav-before', `Before navigation: ${fromUrl}`);
    
    const link = await this.page.$(linkSelector);
    if (!link) {
      console.log(`   ❌ Navigation link not found: ${linkSelector}`);
      return false;
    }
    
    await link.click();
    await this.browserHelper.waitForPageLoad();
    await this.browserHelper.captureAndSave('nav-after', `After navigation: ${this.page.url()}`);
    
    const currentUrl = this.page.url();
    const success = currentUrl.includes(toUrl);
    
    console.log(`   ${success ? '✅' : '❌'} Navigation ${success ? 'successful' : 'failed'}`);
    console.log(`   Current URL: ${currentUrl}`);
    
    return success;
  }

  async highlightElement(selector, color = 'red') {
    await this.page.evaluate((sel, col) => {
      const element = document.querySelector(sel);
      if (element) {
        element.style.border = `3px solid ${col}`;
        element.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
      }
    }, selector, color);
    
    await this.page.waitForTimeout(500);
    await this.browserHelper.captureAndSave('highlighted-element', `Highlighted: ${selector}`);
  }

  async generateDebugReport() {
    const reportPath = path.join(
      path.join(require('os').homedir(), 'Downloads', 'Opencode', 'SurveyProduct'),
      'debug-report.json'
    );
    
    const report = {
      generatedAt: new Date().toISOString(),
      totalAnalyses: this.debugLog.length,
      analyses: this.debugLog
    };
    
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📊 Debug report generated: ${reportPath}`);
    
    return reportPath;
  }

  async checkLayout(viewport, pageName) {
    console.log(`\n📐 Checking layout for ${pageName} at ${viewport.width}x${viewport.height}`);
    
    await this.browserHelper.captureAndSave(
      `layout-${viewport.width}x${viewport.height}-${pageName}`,
      `Layout check: ${pageName} (${viewport.width}x${viewport.height})`
    );
    
    const layoutInfo = await this.page.evaluate(() => {
      return {
        scrollWidth: document.body.scrollWidth,
        scrollHeight: document.body.scrollHeight,
        clientWidth: document.body.clientWidth,
        clientHeight: document.body.clientHeight,
        hasHorizontalScroll: document.body.scrollWidth > document.body.clientWidth,
        hasVerticalScroll: document.body.scrollHeight > document.body.clientHeight
      };
    });
    
    console.log(`   Viewport: ${layoutInfo.clientWidth}x${layoutInfo.clientHeight}`);
    console.log(`   Content: ${layoutInfo.scrollWidth}x${layoutInfo.scrollHeight}`);
    console.log(`   Horizontal scroll: ${layoutInfo.hasHorizontalScroll ? 'Yes ⚠️' : 'No ✅'}`);
    console.log(`   Vertical scroll: ${layoutInfo.hasVerticalScroll ? 'Yes' : 'No'}`);
    
    return layoutInfo;
  }

  async waitForVisualChange(timeout = 5000) {
    console.log(`\n⏳ Waiting for visual changes (timeout: ${timeout}ms)...`);
    
    let previousScreenshot = await this.page.screenshot();
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      await this.page.waitForTimeout(100);
      const currentScreenshot = await this.page.screenshot();
      
      if (!previousScreenshot.equals(currentScreenshot)) {
        console.log('   ✓ Visual change detected');
        await this.browserHelper.captureAndSave('visual-change', 'Visual change detected');
        return true;
      }
      
      previousScreenshot = currentScreenshot;
    }
    
    console.log('   ⏱ No visual change detected within timeout');
    return false;
  }
}

module.exports = { VisualDebugger };
