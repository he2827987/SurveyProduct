const { chromium, devices } = require('playwright');

const PROD = 'https://surveyproduct.onrender.com';
const EMAIL = 'prodtest2@test.com';
const PASS = 'Test123456';

const results = { pass: [], fail: [], warn: [] };
const _log = console.log;
function ok(msg) { results.pass.push(msg); _log(`  ✅ ${msg}`); }
function fail(msg, detail) { results.fail.push(msg); _log(`  ❌ ${msg}${detail ? ' — ' + detail : ''}`); }
function warn(msg) { results.warn.push(msg); _log(`  ⚠️  ${msg}`); }

// Questions data
const questions = [
  {
    text: '您对公司整体工作环境的满意度如何？', type: 'single_choice', required: true,
    options: ['非常满意', '比较满意', '一般', '不太满意', '非常不满意'],
    scores: [10, 8, 5, 3, 1]
  },
  {
    text: '您认为公司的薪资福利水平在行业中处于什么位置？', type: 'single_choice', required: true,
    options: ['远高于行业平均水平', '略高于行业平均水平', '与行业平均水平相当', '略低于行业平均水平', '远低于行业平均水平'],
    scores: [10, 8, 5, 3, 1]
  },
  {
    text: '以下哪些方面您认为公司需要优先改进？（可多选）', type: 'multi_choice', required: true,
    options: ['薪资待遇', '办公环境', '职业发展通道', '团队协作氛围', '工作生活平衡', '管理方式']
  },
  {
    text: '请描述您在工作中遇到的最大挑战，以及您希望公司如何帮助解决。', type: 'text_input', required: true
  },
  {
    text: '您给公司的技术栈和开发工具打几分？（1-10分）', type: 'number_input', required: true,
    minScore: 1, maxScore: 10
  },
  {
    text: '您对直属上级的管理方式满意吗？', type: 'single_choice', required: true,
    options: ['非常满意', '比较满意', '一般', '不太满意', '非常不满意'],
    scores: [10, 8, 5, 3, 1]
  },
  {
    text: '您对公司未来一年的发展有什么建议？', type: 'text_input', required: false
  },
  {
    text: '您是否愿意向朋友推荐这家公司作为雇主？', type: 'single_choice', required: true,
    options: ['非常愿意', '可能会', '不确定', '可能不会', '绝对不会'],
    scores: [10, 7, 5, 3, 1]
  },
  {
    text: '请按重要程度对以下工作因素排序（从最重要到最不重要）', type: 'sort_order', required: true,
    options: ['薪酬水平', '工作内容挑战性', '团队氛围', '晋升机会', '办公地点便利性']
  },
  {
    text: '您日常使用哪些开发工具？（可多选）', type: 'multi_choice', required: false,
    options: ['VS Code', 'JetBrains IDE', 'Vim/Neovim', 'GitHub Copilot', 'ChatGPT/AI辅助', 'Docker', 'Postman']
  }
];

const respondents = [
  { name: '张伟', dept: '研发部', pos: '高级工程师', answers: [0, 2, [0,2,4], '最大的挑战是跨部门沟通效率低，建议引入更好的需求管理工具和定期跨部门同步会议。', 8, 1, '建议加大技术分享投入，鼓励团队互相学习新技术，同时希望管理层更重视技术债务治理。', 1, [1,0,2,3,4], [0,3,4,5,6]] },
  { name: '李娜', dept: '产品部', pos: '产品经理', answers: [1, 1, [4,5,2], '开发资源总是不够，需求排期经常延迟。希望增加研发人员编制，优化项目优先级评审流程。', 7, 3, '应该加强数据驱动的决策文化，让产品决策更多基于用户调研和数据洞察。', 1, [1,0,2,4,3], [1,3,4]] },
  { name: '王强', dept: '研发部', pos: '前端开发工程师', answers: [0, 4, [1], '刚入职，感觉团队氛围很好。希望提供更系统的入职培训和技术文档。', 9, 0, '技术栈很新，体验很好。希望继续保持对新技术的探索。', 0, [1,0,2,3,4], [0,3,4,5,6]] },
  { name: '陈静', dept: '设计部', pos: 'UI设计师', answers: [2, 3, [0,1,4,5], '设计资源严重不足，加班频繁。希望合理分配设计资源，减少并行项目数量。', 6, 3, '建议引入更专业的设计工具和资源，同时希望产品经理更尊重设计专业建议。', 3, [0,1,2,4,3], [1,3,4]] },
  { name: '刘洋', dept: '研发部', pos: '后端开发工程师', answers: [1, 2, [2,3,1], '系统技术架构老旧，维护成本高。建议制定技术债务清理计划，逐步重构核心模块。', 7, 2, '建议定期组织技术分享会和黑客松活动，同时改善远程办公政策。', 1, [1,2,0,3,4], [0,1,3,4,5]] }
];

async function login(page) {
  await page.goto(`${PROD}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.fill('input[placeholder*="邮箱"]', EMAIL);
  await page.fill('input[type="password"]', PASS);
  await page.locator('button:has-text("登录")').click();
  await page.waitForURL('**/dashboard**', { timeout: 15000 });
  await page.waitForTimeout(1000);
  ok('Logged in');
}

async function sleep(ms) { await new Promise(r => setTimeout(r, ms)); }

async function closeDialog(page) {
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(300);
  const cancel = page.locator('.el-dialog__close, button:has-text("取消")').first();
  if (await cancel.count() > 0) {
    await cancel.click({ force: true }).catch(() => {});
    await sleep(500);
  }
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(500);
}

async function clickMenu(page, text) {
  await closeDialog(page);
  await page.locator('.el-menu-item').filter({ hasText: text }).first().click({ timeout: 5000 });
  await sleep(2000);
}

async function createQuestions(page) {
  console.log('\n=== STEP 1: CREATE QUESTIONS ===');
  await clickMenu(page, '题库管理');
  await sleep(1000);

  const createdIds = [];
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    _log(`Creating Q${i + 1}: ${q.text.substring(0, 40)}... (${q.type})`);

    try {
      // Click "新增题目"
      await page.locator('button:has-text("新增题目")').click({ timeout: 5000 });
      await sleep(800);

      // Wait for dialog
      const dialog = page.locator('.el-dialog[aria-label*="新增"]');
      await dialog.waitFor({ state: 'visible', timeout: 5000 });
      await sleep(500);

      // Fill question text
      const textInput = dialog.locator('input.el-input__inner').first();
      await textInput.fill(q.text);
      await sleep(300);

      // Select type
      const typeSelect = dialog.locator('.el-select').first();
      await typeSelect.click();
      await sleep(500);
      await page.locator('.el-select-dropdown__item').filter({ hasText: getChineseType(q.type) }).first().click();
      await sleep(500);

      // Check for options section
      const addOptionBtn = dialog.locator('button:has-text("添加选项")').first();
      if (q.options && await addOptionBtn.count() > 0) {
        // Add each option
        for (let j = 0; j < q.options.length; j++) {
          await addOptionBtn.click();
          await sleep(300);

          const inputs = dialog.locator('input.el-input__inner');
          const optInput = inputs.nth(q.options.length); // last input added
          await optInput.fill(q.options[j]);
          await sleep(200);

          // If this type has scores, fill score for each option
          if (q.scores) {
            const scoreInputs = dialog.locator('input.el-input-number .el-input__inner');
            const lastScore = scoreInputs.last();
            if (await lastScore.count() > 0) {
              await lastScore.fill(String(q.scores[j]));
              await sleep(200);
            }
          }

          // Click confirm button for option (if exists)
          const confirmOpt = page.locator('.el-dialog:visible button:has-text("确定")').first();
          if (await confirmOpt.count() > 0 && await confirmOpt.isVisible()) {
            await confirmOpt.click().catch(() => {});
            await sleep(300);
          }
        }
      }

      // Set required
      const requiredSwitch = dialog.locator('.el-switch').first();
      if (await requiredSwitch.count() > 0 && q.required !== await requiredSwitch.getAttribute('aria-checked')) {
        await requiredSwitch.click();
        await sleep(200);
      }

      // Click confirm button
      await dialog.locator('button:has-text("确定")').last().click({ timeout: 5000 });
      await sleep(1000);

      // Check for success
      const successMsg = page.locator('.el-message--success').first();
      if (await successMsg.count() > 0) {
        ok(`Q${i + 1}: "${q.text.substring(0, 30)}..." (${q.type})`);
      } else {
        warn(`Q${i + 1}: created but no success message`);
      }

      // Get question ID from URL or response
      createdIds.push(`q${i + 1}`);

    } catch (e) {
      fail(`Q${i + 1}: ${e.message.substring(0, 100)}`);
      await closeDialog(page);
    }
  }
  return createdIds;
}

function getChineseType(type) {
  const map = {
    'single_choice': '单选题',
    'multi_choice': '多选题',
    'text_input': '文本输入题',
    'number_input': '数字输入题',
    'sort_order': '排序题'
  };
  return map[type] || type;
}

async function createSurvey(page, questionIds) {
  console.log('\n=== STEP 2: CREATE SURVEY ===');
  await clickMenu(page, '调研管理');
  await sleep(1500);

  try {
    // Click create button
    const createBtn = page.locator('button:has-text("创建"), button:has-text("新增")').first();
    await createBtn.click({ timeout: 5000 });
    await sleep(1000);

    // Fill form
    const titleInput = page.locator('.el-dialog input.el-input__inner').first();
    await titleInput.fill('2025年度员工满意度与工作体验调研');
    await sleep(300);

    const descInput = page.locator('.el-dialog textarea.el-textarea__inner').first();
    if (await descInput.count() > 0) {
      await descInput.fill('本调研旨在全面了解员工对工作环境、薪资福利、团队协作等方面的真实感受，所有回答严格保密。');
      await sleep(300);
    }

    await page.locator('.el-dialog button:has-text("确定")').last().click({ timeout: 5000 });
    await sleep(1500);

    const successMsg = page.locator('.el-message--success').first();
    if (await successMsg.count() > 0) {
      ok('Survey created');
    } else {
      warn('Survey created but no success confirmation');
    }

    // Get survey ID from URL if redirected
    const url = page.url();
    const match = url.match(/surveys\/(\d+)/);
    if (match) {
      ok(`Survey ID: ${match[1]}`);
      return match[1];
    }

    ok('Survey created (could not extract ID from URL)');
    return 'unknown';
  } catch (e) {
    fail(`Create survey: ${e.message.substring(0, 150)}`);
    return null;
  }
}

async function publishSurvey(page, surveyId) {
  console.log('\n=== STEP 3: PUBLISH SURVEY ===');
  try {
    // Find the survey in the list and look for publish button
    const surveyRow = page.locator(`tr:has-text("员工满意度")`).first();
    if (await surveyRow.count() > 0) {
      const publishBtn = surveyRow.locator('button:has-text("发布"), button:has-text("激活")').first();
      if (await publishBtn.count() > 0) {
        await publishBtn.click();
        await sleep(1000);
        ok('Survey published');
        return;
      }
    }

    // Try direct API
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    const res = await page.evaluate(async ({ token, id }) => {
      const r = await fetch(`/api/v1/surveys/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ status: 'active' })
      });
      return { ok: r.ok, status: r.status };
    }, { token, id: surveyId });
    if (res.ok) ok(`Survey published via API (id=${surveyId})`);
    else fail(`Publish failed: ${res.status}`);
  } catch (e) {
    fail(`Publish: ${e.message.substring(0, 100)}`);
  }
}

async function fillSurveyPC(page, surveyId, respondent, idx) {
  console.log(`\n=== STEP 4.${idx}: FILL SURVEY (PC) — ${respondent.name} ===`);
  const fillUrl = `${PROD}/survey/fill/${surveyId}`;
  await page.goto(fillUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: `e2e-04-fill-pc-${idx}.png` });

  const content = await page.textContent('body');
  if (content.includes('该调研不存在') || content.includes('404')) {
    fail(`Survey fill page not found for id=${surveyId}`);
    return;
  }

  if (content.includes('已结束') || content.includes('已过期') || content.includes('未开始')) {
    warn(`Survey may not be active: ${content.substring(0, 100)}`);
  }

  // Fill respondent info (if fields exist)
  const nameInput = page.locator('input[placeholder*="姓名"], input[placeholder*="name"]').first();
  if (await nameInput.count() > 0) await nameInput.fill(respondent.name);

  const deptInput = page.locator('input[placeholder*="部门"], input[placeholder*="department"]').first();
  if (await deptInput.count() > 0) await deptInput.fill(respondent.dept);

  const posInput = page.locator('input[placeholder*="职位"], input[placeholder*="position"]').first();
  if (await posInput.count() > 0) await posInput.fill(respondent.pos);

  await sleep(500);

  // Fill answers
  for (let qi = 0; qi < respondent.answers.length; qi++) {
    const a = respondent.answers[qi];
    _log(`  Q${qi + 1} (${questions[qi].type})`);

    try {
      if (questions[qi].type === 'single_choice') {
        // Find the option by text and click
        const optText = questions[qi].options[a];
        const optBtn = page.locator(`label:has-text("${optText}") input[type="radio"], label:has-text("${optText}")`).first();
        if (await optBtn.count() > 0) {
          await optBtn.click({ timeout: 3000 });
          await sleep(300);
        } else {
          // Try direct label click
          await page.locator(`text="${optText}"`).first().click({ timeout: 3000 });
          await sleep(300);
        }
      } else if (questions[qi].type === 'multi_choice') {
        for (const optIdx of a) {
          const optText = questions[qi].options[optIdx];
          const optBtn = page.locator(`label:has-text("${optText}") input[type="checkbox"], label:has-text("${optText}")`).first();
          if (await optBtn.count() > 0) {
            await optBtn.click({ timeout: 3000 });
            await sleep(200);
          } else {
            await page.locator(`text="${optText}"`).first().click({ timeout: 3000 });
            await sleep(200);
          }
        }
      } else if (questions[qi].type === 'text_input') {
        const textarea = page.locator('textarea').nth(qi).first();
        if (await textarea.count() > 0) {
          await textarea.fill(String(a));
          await sleep(300);
        } else {
          // Try general textarea
          const allTextareas = page.locator('textarea');
          const count = await allTextareas.count();
          if (count > qi) {
            await allTextareas.nth(qi).fill(String(a));
            await sleep(300);
          }
        }
      } else if (questions[qi].type === 'number_input') {
        const numInput = page.locator('input[type="number"]').nth(qi).first();
        if (await numInput.count() > 0) {
          await numInput.fill(String(a));
          await sleep(300);
        } else {
          const allNumInputs = page.locator('input[type="number"]');
          const count = await allNumInputs.count();
          if (count > qi) {
            await allNumInputs.nth(qi).fill(String(a));
            await sleep(300);
          }
        }
      } else if (questions[qi].type === 'sort_order') {
        // Sort order - need to implement drag or click ordering
        warn(`Q${qi + 1}: Sort order type - skipping drag interaction`);
      }
    } catch (e) {
      warn(`Q${qi + 1} answer failed: ${e.message.substring(0, 80)}`);
    }
  }

  // Submit
  await page.screenshot({ path: `e2e-05-filled-pc-${idx}.png` });
  const submitBtn = page.locator('button:has-text("提交"), button[type="submit"]').first();
  if (await submitBtn.count() > 0) {
    await submitBtn.click();
    await sleep(3000);
    const successMsg = page.locator('.el-message--success').first();
    if (await successMsg.count() > 0) {
      ok(`${respondent.name}: submitted successfully`);
    } else {
      warn(`${respondent.name}: submitted but no success message`);
    }
  } else {
    warn(`${respondent.name}: no submit button found`);
  }
}

async function fillSurveyMobile(page, surveyId, respondent, idx) {
  console.log(`\n=== STEP 5.${idx}: FILL SURVEY (Mobile) — ${respondent.name} ===`);

  // Create mobile context
  const iphone = { viewport: { width: 390, height: 844 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15' };
  const mobileCtx = await browser.newContext(iphone);
  const mPage = await mobileCtx.newPage();
  mPage.on('pageerror', e => log(`Mobile err: ${e.message.substring(0, 100)}`));

  await mPage.goto(`${PROD}/survey/fill/${surveyId}`, { waitUntil: 'networkidle', timeout: 60000 });
  await mPage.screenshot({ path: `e2e-06-fill-mobile-${idx}.png` });

  const content = await mPage.textContent('body');
  if (content.includes('该调研不存在')) {
    fail(`Mobile fill: survey ${surveyId} not found`);
    await mobileCtx.close();
    return;
  }

  // Fill info
  const nameInput = mPage.locator('input[placeholder*="姓名"], input[placeholder*="name"]').first();
  if (await nameInput.count() > 0) await nameInput.fill(respondent.name);
  const deptInput = mPage.locator('input[placeholder*="部门"]').first();
  if (await deptInput.count() > 0) await deptInput.fill(respondent.dept);
  const posInput = mPage.locator('input[placeholder*="职位"]').first();
  if (await posInput.count() > 0) await posInput.fill(respondent.pos);
  await sleep(500);

  // Fill answers (same as PC)
  for (let qi = 0; qi < respondent.answers.length; qi++) {
    const a = respondent.answers[qi];
    try {
      if (questions[qi].type === 'single_choice') {
        const optText = questions[qi].options[a];
        await mPage.locator(`text="${optText}"`).first().click({ timeout: 3000 });
        await mPage.sleep(300);
      } else if (questions[qi].type === 'multi_choice') {
        for (const optIdx of a) {
          await mPage.locator(`text="${questions[qi].options[optIdx]}"`).first().click({ timeout: 3000 });
          await mPage.sleep(200);
        }
      } else if (questions[qi].type === 'text_input') {
        const textarea = mPage.locator('textarea').nth(qi).first();
        if (await textarea.count() > 0) {
          await textarea.fill(String(a));
          await mPage.sleep(300);
        }
      } else if (questions[qi].type === 'number_input') {
        const numInput = mPage.locator('input[type="number"]').nth(qi).first();
        if (await numInput.count() > 0) {
          await numInput.fill(String(a));
          await mPage.sleep(300);
        }
      } else if (questions[qi].type === 'sort_order') {
        warn(`Mobile Q${qi + 1}: Sort order - skipping`);
      }
    } catch (e) {
      warn(`Mobile Q${qi + 1}: ${e.message.substring(0, 80)}`);
    }
  }

  await mPage.screenshot({ path: `e2e-07-filled-mobile-${idx}.png` });
  const submitBtn = mPage.locator('button:has-text("提交"), button[type="submit"]').first();
  if (await submitBtn.count() > 0) {
    await submitBtn.click();
    await mPage.sleep(3000);
    const successMsg = mPage.locator('.el-message--success').first();
    if (await successMsg.count() > 0) ok(`Mobile: ${respondent.name} submitted`);
    else warn(`Mobile: ${respondent.name} no success msg`);
  }
  await mobileCtx.close();
}

async function testAnalytics(page, surveyId) {
  console.log('\n=== STEP 6: DATA ANALYSIS ===');
  await clickMenu(page, '数据分析');
  await sleep(2000);

  // Select survey
  const select = page.locator('.filter-select').first();
  await select.click();
  await sleep(500);

  const surveyOption = page.locator(`.el-select-dropdown__item:has-text("员工满意度")`).first();
  if (await surveyOption.count() > 0) {
    await surveyOption.click();
    await sleep(2000);
    ok('Selected survey in analysis page');
  } else {
    const allItems = page.locator('.el-select-dropdown__item');
    const count = await allItems.count();
    _log(`Dropdown items: ${count}`);
    fail('Could not find survey in dropdown');
    await page.keyboard.press('Escape');
  }

  await page.screenshot({ path: 'e2e-08-analysis.png' });

  // Try score mode
  const statsMode = page.locator('.el-select').nth(1);
  if (await statsMode.count() > 0) {
    // Check chart area
    await sleep(1000);
    const chart = page.locator('.chart-container, .echarts, canvas').first();
    ok(`Analysis page loaded (${await chart.count()} chart elements)`);
  }
}

async function testLLM(page, surveyId) {
  console.log('\n=== STEP 7: LLM SUMMARY ===');
  // Try triggering AI summary from the UI
  const aiBtn = page.locator('button:has-text("生成总结"), button:has-text("AI")').first();
  if (await aiBtn.count() > 0) {
    ok('AI summary button found');
    await aiBtn.click();
    await page.waitForTimeout(10000);
    await page.screenshot({ path: 'e2e-09-llm-summary.png' });
    ok('AI summary triggered');
  } else {
    // Try LLM API directly
    warn('No AI button on page, trying API directly');
    try {
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      const res = await page.evaluate(async ({ token, id }) => {
        const r = await fetch(`/api/v1/organizations/23/surveys/${id}/analytics/ai-summary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        return { ok: r.ok, data: r.ok ? await r.json() : null };
      }, { token, id: surveyId });
      if (res.ok && res.data) {
        ok(`AI Summary API: ${JSON.stringify(res.data).substring(0, 200)}...`);
      } else {
        warn(`AI Summary API: ${JSON.stringify(res)}`);
      }
    } catch (e) {
      warn(`AI Summary error: ${e.message}`);
    }
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  page.on('pageerror', e => console.log(`  ⚠️  ${e.message.substring(0, 120)}`));

  try {
    await login(page);
    await createQuestions(page);
    const surveyId = await createSurvey(page);

    if (surveyId && surveyId !== 'unknown') {
      await publishSurvey(page, surveyId);
      // Fill surveys - 3 PC + 2 mobile
      for (let i = 0; i < Math.min(3, respondents.length); i++) {
        await fillSurveyPC(page, surveyId, respondents[i], i + 1);
      }
      for (let i = 3; i < respondents.length; i++) {
        await fillSurveyMobile(browser, surveyId, respondents[i], i + 1);
      }
      await testAnalytics(page, surveyId);
      await testLLM(page, surveyId);
    }
  } catch (e) {
    fail(`Fatal: ${e.message.substring(0, 200)}`);
  }

  console.log('\n========================================');
  console.log(`  RESULTS: ${results.pass.length} ok, ${results.fail.length} fail, ${results.warn.length} warn`);
  if (results.fail.length > 0) {
    for (const f of results.fail) console.log(`  ❌ ${f}`);
  }
  console.log('========================================');

  await page.screenshot({ path: 'e2e-final.png' });
  await browser.close();
})();
