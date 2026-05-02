const BASE = 'https://surveyproduct.onrender.com/api/v1';

const EMAIL = 'prodtest2@test.com';
const PASSWORD = 'Test123456';

let TOKEN = '';
let SURVEY_ID = null;

async function api(method, path, body = null, headers = {}) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', ...headers },
  };
  if (TOKEN) opts.headers['Authorization'] = `Bearer ${TOKEN}`;
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    const err = new Error(`${method} ${path} → ${res.status}: ${text.substring(0, 200)}`);
    err.status = res.status;
    throw err;
  }
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('text/csv') || ct.includes('octet-stream')) return res;
  return res.json();
}

function log(msg) { console.log(`  ${msg}`); }
function logOk(msg) { console.log(`  ✅ ${msg}`); }
function logFail(msg) { console.log(`  ❌ ${msg}`); }

// ==============================
// STEP 0: Login
// ==============================
async function login() {
  console.log('\n=== STEP 0: Login ===');
  const formData = new FormData();
  formData.append('username', EMAIL);
  formData.append('password', PASSWORD);
  const res = await fetch(`${BASE}/users/login/access-token`, { method: 'POST', body: formData });
  const data = await res.json();
  TOKEN = data.access_token;
  if (!TOKEN) throw new Error('Login failed: no token');
  logOk(`Logged in as ${EMAIL}`);
}

// ==============================
// STEP 1: Create Questions
// ==============================
const questions = [
  // Q1: single_choice with scores
  {
    text: '您对公司整体工作环境的满意度如何？',
    type: 'single_choice',
    options: [
      { text: '非常满意', score: 10 },
      { text: '比较满意', score: 8 },
      { text: '一般', score: 5 },
      { text: '不太满意', score: 3 },
      { text: '非常不满意', score: 1 }
    ],
    min_score: 1,
    max_score: 10,
    is_required: true
  },
  // Q2: single_choice
  {
    text: '您认为公司的薪资福利水平在行业中处于什么位置？',
    type: 'single_choice',
    options: [
      { text: '远高于行业平均水平', score: 10 },
      { text: '略高于行业平均水平', score: 8 },
      { text: '与行业平均水平相当', score: 5 },
      { text: '略低于行业平均水平', score: 3 },
      { text: '远低于行业平均水平', score: 1 }
    ],
    min_score: 1,
    max_score: 10,
    is_required: true
  },
  // Q3: multi_choice
  {
    text: '以下哪些方面您认为公司需要优先改进？（可多选）',
    type: 'multi_choice',
    options: [
      { text: '薪资待遇' },
      { text: '办公环境' },
      { text: '职业发展通道' },
      { text: '团队协作氛围' },
      { text: '工作生活平衡' },
      { text: '管理方式' }
    ],
    is_required: true
  },
  // Q4: text_input (subjective - for LLM summary)
  {
    text: '请描述您在工作中遇到的最大挑战，以及您希望公司如何帮助解决。',
    type: 'text_input',
    is_required: true
  },
  // Q5: number_input
  {
    text: '您给公司的技术栈和开发工具打几分？（1-10分）',
    type: 'number_input',
    min_score: 1,
    max_score: 10,
    is_required: true
  },
  // Q6: single_choice
  {
    text: '您对直属上级的管理方式满意吗？',
    type: 'single_choice',
    options: [
      { text: '非常满意', score: 10 },
      { text: '比较满意', score: 8 },
      { text: '一般', score: 5 },
      { text: '不太满意', score: 3 },
      { text: '非常不满意', score: 1 }
    ],
    min_score: 1,
    max_score: 10,
    is_required: true
  },
  // Q7: text_input (subjective - for LLM)
  {
    text: '您对公司未来一年的发展有什么建议？',
    type: 'text_input',
    is_required: false
  },
  // Q8: single_choice
  {
    text: '您是否愿意向朋友推荐这家公司作为雇主？',
    type: 'single_choice',
    options: [
      { text: '非常愿意', score: 10 },
      { text: '可能会', score: 7 },
      { text: '不确定', score: 5 },
      { text: '可能不会', score: 3 },
      { text: '绝对不会', score: 1 }
    ],
    min_score: 1,
    max_score: 10,
    is_required: true
  },
  // Q9: sort_order
  {
    text: '请按重要程度对以下工作因素进行排序（从最重要到最不重要）',
    type: 'sort_order',
    options: [
      { text: '薪酬水平' },
      { text: '工作内容挑战性' },
      { text: '团队氛围' },
      { text: '晋升机会' },
      { text: '办公地点便利性' }
    ],
    is_required: true
  },
  // Q10: multi_choice
  {
    text: '您日常使用哪些开发工具？（可多选）',
    type: 'multi_choice',
    options: [
      { text: 'VS Code' },
      { text: 'JetBrains IDE' },
      { text: 'Vim/Neovim' },
      { text: 'GitHub Copilot' },
      { text: 'ChatGPT/AI辅助' },
      { text: 'Docker' },
      { text: 'Postman' }
    ],
    is_required: false
  }
];

async function createQuestions() {
  console.log('\n=== STEP 1: Create Questions ===');
  // First create a survey to attach questions to
  const survey = await api('POST', '/surveys/', {
    title: '2025年度员工满意度与工作体验调研',
    description: '本调研旨在全面了解员工对工作环境、薪资福利、团队协作、管理方式等方面的真实感受，为持续改善工作体验提供数据支撑。所有回答将严格保密。'
  });
  SURVEY_ID = survey.id;
  logOk(`Created survey: "${survey.title}" (id=${survey.id})`);

  const questionIds = [];
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    try {
      const created = await api('POST', `/surveys/${SURVEY_ID}/questions/`, {
        text: q.text,
        type: q.type,
        options: q.options || undefined,
        min_score: q.min_score,
        max_score: q.max_score,
        is_required: q.is_required,
        order: i + 1
      });
      questionIds.push(created.id);
      logOk(`Q${i + 1} (${q.type}): "${q.text.substring(0, 40)}..." → id=${created.id}`);
    } catch (e) {
      logFail(`Q${i + 1} failed: ${e.message}`);
    }
  }

  // Update survey to link questions
  try {
    await api('PUT', `/surveys/${SURVEY_ID}`, {
      question_ids: questionIds
    });
    logOk(`Linked ${questionIds.length} questions to survey`);
  } catch (e) {
    logFail(`Link questions failed: ${e.message}`);
  }

  return questionIds;
}

// ==============================
// STEP 2: Publish Survey
// ==============================
async function publishSurvey() {
  console.log('\n=== STEP 2: Publish Survey ===');
  try {
    await api('POST', `/surveys/${SURVEY_ID}/status`, {
      status: 'active'
    });
    logOk(`Survey ${SURVEY_ID} published`);
  } catch (e) {
    logFail(`Publish failed: ${e.message}`);
  }
}

// ==============================
// STEP 3: Fill Survey (3 different respondents)
// ==============================
const respondents = [
  {
    name: '张伟',
    department: '研发部',
    position: '高级工程师',
    answers: {
      1: '非常满意',
      2: '与行业平均水平相当',
      3: ['薪资待遇', '职业发展通道', '工作生活平衡'],
      4: '最大的挑战是跨部门沟通效率低，很多需求变更需要反复对齐，建议引入更好的需求管理工具和定期的跨部门同步会议。',
      5: 8,
      6: '比较满意',
      7: '建议加大技术分享的投入，鼓励团队之间互相学习新技术，同时希望管理层能更重视技术债务的治理。',
      8: '可能会',
      9: ['工作内容挑战性', '团队氛围', '薪酬水平', '晋升机会', '办公地点便利性'],
      10: ['VS Code', 'GitHub Copilot', 'ChatGPT/AI辅助', 'Docker', 'Postman']
    }
  },
  {
    name: '李娜',
    department: '产品部',
    position: '产品经理',
    answers: {
      1: '比较满意',
      2: '略高于行业平均水平',
      3: ['工作生活平衡', '管理方式', '办公环境'],
      4: '作为产品经理，感觉开发资源总是不够，需求排期经常延迟。希望公司能增加研发人员编制，并优化项目优先级评审流程。',
      5: 7,
      6: '一般',
      7: '公司应该加强数据驱动的决策文化，让产品决策更多基于用户调研和数据洞察，而非仅凭直觉。',
      8: '非常愿意',
      9: ['工作内容挑战性', '薪酬水平', '晋升机会', '团队氛围', '办公地点便利性'],
      10: ['JetBrains IDE', 'GitHub Copilot', 'ChatGPT/AI辅助', 'Postman']
    }
  },
  {
    name: '王强',
    department: '研发部',
    position: '前端开发工程师',
    answers: {
      1: '非常满意',
      2: '远高于行业平均水平',
      3: ['办公环境', '团队协作氛围'],
      4: '刚入职不久，感觉团队氛围很好，老同事都很乐意帮助新人。不过希望公司能提供更系统的入职培训和技术文档。',
      5: 9,
      6: '非常满意',
      7: '技术栈很新，开发工具齐全，体验很好。希望继续保持对新技术的探索和应用。',
      8: '非常愿意',
      9: ['团队氛围', '工作内容挑战性', '薪酬水平', '晋升机会', '办公地点便利性'],
      10: ['VS Code', 'GitHub Copilot', 'ChatGPT/AI辅助', 'Docker', 'Vim/Neovim', 'Postman']
    }
  },
  {
    name: '陈静',
    department: '设计部',
    position: 'UI设计师',
    answers: {
      1: '一般',
      2: '略低于行业平均水平',
      3: ['薪资待遇', '职业发展通道', '工作生活平衡', '管理方式'],
      4: '设计资源和人手严重不足，经常需要一个人同时负责多个项目。加班比较频繁，希望能合理分配设计资源，减少并行项目的数量。',
      5: 6,
      6: '不太满意',
      7: '建议引入更专业的设计工具和资源，同时希望产品经理在需求评审时能更尊重设计的专业建议。',
      8: '不确定',
      9: ['薪酬水平', '工作内容挑战性', '团队氛围', '办公地点便利性', '晋升机会'],
      10: ['JetBrains IDE', 'ChatGPT/AI辅助', 'Docker', 'Postman']
    }
  },
  {
    name: '刘洋',
    department: '研发部',
    position: '后端开发工程师',
    answers: {
      1: '比较满意',
      2: '与行业平均水平相当',
      3: ['职业发展通道', '团队协作氛围', '办公环境'],
      4: '系统的技术架构有些老旧，维护成本越来越高。建议制定技术债务清理计划，逐步重构核心模块，同时引入微服务架构。',
      5: 7,
      6: '一般',
      7: '公司应该定期组织技术分享会和黑客松活动，激发团队创新精神。另外希望改善远程办公的政策和设备支持。',
      8: '可能会',
      9: ['工作内容挑战性', '团队氛围', '薪酬水平', '晋升机会', '办公地点便利性'],
      10: ['VS Code', 'GitHub Copilot', 'ChatGPT/AI辅助', 'Docker', 'JetBrains IDE', 'Postman']
    }
  }
];

async function fillSurveys() {
  console.log('\n=== STEP 3: Fill Surveys ===');
  for (const r of respondents) {
    try {
      const result = await api('POST', `/surveys/${SURVEY_ID}/answers/`, {
        answers: r.answers,
        respondent_name: r.name,
        respondent_department: r.department,
        respondent_position: r.position
      });
      logOk(`${r.name} (${r.department}/${r.position}) → score=${result.total_score || 'N/A'} id=${result.id}`);
    } catch (e) {
      logFail(`${r.name}: ${e.message}`);
    }
  }
}

// ==============================
// STEP 4: Verify Data
// ==============================
async function verifyData() {
  console.log('\n=== STEP 4: Verify Data ===');
  try {
    const stats = await api('GET', `/surveys/${SURVEY_ID}/statistics`);
    logOk(`Survey stats: ${JSON.stringify(stats)}`);
  } catch (e) {
    logFail(`Stats failed: ${e.message}`);
  }

  try {
    const answers = await api('GET', `/surveys/${SURVEY_ID}/answers/`, null);
    const list = Array.isArray(answers) ? answers : (answers?.items || []);
    logOk(`Total answers: ${list.length}`);
  } catch (e) {
    logFail(`Answers list failed: ${e.message}`);
  }
}

// ==============================
// STEP 5: Test Analysis API
// ==============================
async function testAnalytics() {
  console.log('\n=== STEP 5: Data Analysis ===');

  // Get user info to know organization
  let orgId = 23;
  try {
    const user = await api('GET', '/users/me');
    logOk(`User: ${user.username}, org_id=${user.organization_id}`);
    if (user.organization_id) orgId = user.organization_id;
  } catch (e) {
    log(`User info failed: ${e.message}`);
  }

  // Department analytics
  try {
    const dept = await api('GET', `/organizations/${orgId}/surveys/${SURVEY_ID}/analytics`, { dimension: 'department' });
    logOk(`Department analytics: ${JSON.stringify(dept).substring(0, 200)}...`);
  } catch (e) {
    logFail(`Department analytics: ${e.message}`);
  }

  // Question scores
  try {
    const scores = await api('GET', `/organizations/${orgId}/surveys/${SURVEY_ID}/analytics`);
    logOk(`Survey analytics loaded successfully`);
  } catch (e) {
    logFail(`Survey analytics: ${e.message}`);
  }
}

// ==============================
// STEP 6: Test LLM Summary
// ==============================
async function testLLMSummary() {
  console.log('\n=== STEP 6: LLM Summary ===');

  // Try AI summary
  try {
    const summary = await api('GET', `/organizations/23/surveys/${SURVEY_ID}/analytics/ai-summary`, null);
    logOk(`AI Summary generated: ${JSON.stringify(summary).substring(0, 300)}...`);
  } catch (e) {
    log(`AI Summary (may need API key): ${e.message}`);
  }

  // Try LLM summarize answers for Q4 (text_input)
  try {
    const answers = await api('GET', `/surveys/${SURVEY_ID}/answers/`, null);
    const answerList = Array.isArray(answers) ? answers : (answers?.items || []);
    
    // Collect Q4 answers
    const q4Answers = [];
    for (const a of answerList) {
      const parsed = typeof a.answers === 'string' ? JSON.parse(a.answers) : a.answers;
      if (parsed['4']) {
        q4Answers.push(parsed['4']);
      }
    }

    if (q4Answers.length > 0) {
      const llmResult = await api('POST', '/llm/summarize_answers', {
        question_text: '请描述您在工作中遇到的最大挑战，以及您希望公司如何帮助解决。',
        answers: q4Answers
      });
      logOk(`LLM Answer Summary: ${JSON.stringify(llmResult).substring(0, 300)}...`);
    } else {
      log('No Q4 answers found for LLM summary');
    }
  } catch (e) {
    log(`LLM summarize answers: ${e.message}`);
  }

  // Try generate_survey_summary
  try {
    const surveyResult = await api('POST', '/llm/generate_survey_summary', {
      survey_data: {
        title: '2025年度员工满意度与工作体验调研',
        total_answers: 5,
        answers: respondents.map(r => r.answers)
      }
    });
    logOk(`Survey Summary: ${JSON.stringify(surveyResult).substring(0, 500)}...`);
  } catch (e) {
    log(`LLM survey summary: ${e.message}`);
  }
}

// ==============================
// MAIN
// ==============================
async function main() {
  console.log('==========================================');
  console.log('  E2E FULL FLOW TEST');
  console.log('==========================================');

  await login();
  const qIds = await createQuestions();
  await publishSurvey();
  await fillSurveys();
  await verifyData();
  await testAnalytics();
  await testLLMSummary();

  console.log('\n==========================================');
  console.log(`  DONE! Survey ID: ${SURVEY_ID}`);
  console.log('==========================================');
}

main().catch(e => {
  console.error('\nFATAL:', e.message);
  process.exit(1);
});
