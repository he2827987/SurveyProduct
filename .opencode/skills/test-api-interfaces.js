const { chromium } = require('playwright');
const fs = require('fs');

/**
 * API 测试配置
 */
const BASE_URL = 'http://localhost:8000';
const DOCS_URL = `${BASE_URL}/docs`;

/**
 * 测试结果存储
 */
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

/**
 * 测试用户数据
 */
const testUser = {
  username: `testuser_${Date.now()}`,
  email: `test_${Date.now()}@example.com`,
  password: 'TestPass123!',
  full_name: 'Test User'
};

/**
 * 存储认证 token
 */
let authToken = null;

/**
 * 工具函数：记录测试结果
 */
function recordTest(endpoint, method, status, message, details = {}) {
  const test = {
    endpoint,
    method,
    status,
    message,
    timestamp: new Date().toISOString(),
    details
  };
  
  testResults.tests.push(test);
  testResults.summary.total++;
  
  if (status === 'PASS') {
    testResults.summary.passed++;
    console.log(`✅ [PASS] ${method} ${endpoint} - ${message}`);
  } else if (status === 'FAIL') {
    testResults.summary.failed++;
    console.log(`❌ [FAIL] ${method} ${endpoint} - ${message}`);
  } else {
    testResults.summary.skipped++;
    console.log(`⚠️  [SKIP] ${method} ${endpoint} - ${message}`);
  }
}

/**
 * 工具函数：发送 HTTP 请求
 */
async function makeRequest(url, options = {}) {
  const https = require('https');
  const http = require('http');
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  if (authToken) {
    defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  const mergedOptions = { ...defaultOptions, ...options };
  
  return new Promise((resolve) => {
    const urlObj = new URL(url);
    const client = urlObj.protocol === 'https:' ? https : http;
    
    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: mergedOptions.method,
      headers: mergedOptions.headers
    };
    
    const req = client.request(reqOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({
            status: res.statusCode,
            ok: res.statusCode >= 200 && res.statusCode < 300,
            data: jsonData
          });
        } catch (error) {
          resolve({
            status: res.statusCode,
            ok: res.statusCode >= 200 && res.statusCode < 300,
            data: data || null
          });
        }
      });
    });
    
    req.on('error', (error) => {
      resolve({
        status: 0,
        ok: false,
        error: error.message
      });
    });
    
    if (mergedOptions.body) {
      req.write(mergedOptions.body);
    }
    
    req.end();
  });
}

/**
 * 测试1：健康检查
 */
async function testHealthCheck() {
  console.log('\n📋 测试 1: 健康检查');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/test`);
  
  if (response.ok && response.data && response.data.message) {
    recordTest('/test', 'GET', 'PASS', '服务器健康检查通过', response.data);
    return true;
  } else {
    recordTest('/test', 'GET', 'FAIL', `服务器健康检查失败: ${response.error || '未知错误'}`, response);
    return false;
  }
}

/**
 * 测试2：用户注册
 */
async function testUserRegistration() {
  console.log('\n📋 测试 2: 用户注册');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/users/register`, {
    method: 'POST',
    body: JSON.stringify(testUser)
  });
  
  if (response.ok || response.status === 201) {
    recordTest('/api/v1/users/register', 'POST', 'PASS', 
      `用户注册成功: ${testUser.username}`, response.data);
    return true;
  } else if (response.status === 400) {
    recordTest('/api/v1/users/register', 'POST', 'SKIP', 
      '用户可能已存在，跳过注册', response.data);
    return true;
  } else {
    recordTest('/api/v1/users/register', 'POST', 'FAIL', 
      `用户注册失败: ${response.error || JSON.stringify(response.data)}`, response);
    return false;
  }
}

/**
 * 测试3：用户登录
 */
async function testUserLogin() {
  console.log('\n📋 测试 3: 用户登录');
  console.log('='.repeat(60));
  
  // 构造表单数据
  const formData = new URLSearchParams();
  formData.append('username', testUser.username);
  formData.append('password', testUser.password);
  
  const response = await makeRequest(`${BASE_URL}/api/v1/users/login/access-token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData.toString()
  });
  
  if (response.ok && response.data && response.data.access_token) {
    authToken = response.data.access_token;
    recordTest('/api/v1/users/login/access-token', 'POST', 'PASS', 
      '用户登录成功，已获取认证 token', { token_type: response.data.token_type });
    return true;
  } else {
    recordTest('/api/v1/users/login/access-token', 'POST', 'FAIL', 
      `用户登录失败: ${response.error || JSON.stringify(response.data)}`, response);
    return false;
  }
}

/**
 * 测试4：获取当前用户信息
 */
async function testGetCurrentUser() {
  console.log('\n📋 测试 4: 获取当前用户信息');
  console.log('='.repeat(60));
  
  if (!authToken) {
    recordTest('/api/v1/users/me', 'GET', 'SKIP', '需要认证，跳过测试');
    return false;
  }
  
  const response = await makeRequest(`${BASE_URL}/api/v1/users/me`);
  
  if (response.ok && response.data) {
    recordTest('/api/v1/users/me', 'GET', 'PASS', 
      `获取用户信息成功: ${response.data.username || response.data.email}`, response.data);
    return true;
  } else {
    recordTest('/api/v1/users/me', 'GET', 'FAIL', 
      `获取用户信息失败: ${response.error || JSON.stringify(response.data)}`, response);
    return false;
  }
}

/**
 * 测试5：组织管理
 */
async function testOrganizations() {
  console.log('\n📋 测试 5: 组织管理');
  console.log('='.repeat(60));
  
  // 测试获取组织列表
  const listResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/`);
  
  if (listResponse.ok) {
    recordTest('/api/v1/organizations/', 'GET', 'PASS', 
      `获取组织列表成功，共 ${listResponse.data?.length || 0} 个组织`, 
      { count: listResponse.data?.length });
    
    // 如果有组织，测试获取单个组织
    if (listResponse.data && listResponse.data.length > 0) {
      const orgId = listResponse.data[0].id;
      const detailResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/${orgId}`);
      
      if (detailResponse.ok) {
        recordTest(`/api/v1/organizations/${orgId}`, 'GET', 'PASS', 
          `获取组织详情成功: ${detailResponse.data?.name || orgId}`, detailResponse.data);
      } else {
        recordTest(`/api/v1/organizations/${orgId}`, 'GET', 'FAIL', 
          '获取组织详情失败', detailResponse);
      }
    }
  } else {
    recordTest('/api/v1/organizations/', 'GET', 'FAIL', 
      '获取组织列表失败', listResponse);
  }
}

/**
 * 测试6：问卷管理
 */
async function testSurveys() {
  console.log('\n📋 测试 6: 问卷管理');
  console.log('='.repeat(60));
  
  // 测试获取问卷列表
  const listResponse = await makeRequest(`${BASE_URL}/api/v1/surveys/`);
  
  if (listResponse.ok) {
    recordTest('/api/v1/surveys/', 'GET', 'PASS', 
      `获取问卷列表成功，共 ${listResponse.data?.length || 0} 个问卷`, 
      { count: listResponse.data?.length });
    
    // 如果有问卷，测试获取单个问卷
    if (listResponse.data && listResponse.data.length > 0) {
      const surveyId = listResponse.data[0].id;
      const detailResponse = await makeRequest(`${BASE_URL}/api/v1/surveys/${surveyId}`);
      
      if (detailResponse.ok) {
        recordTest(`/api/v1/surveys/${surveyId}`, 'GET', 'PASS', 
          `获取问卷详情成功: ${detailResponse.data?.title || surveyId}`, detailResponse.data);
      } else {
        recordTest(`/api/v1/surveys/${surveyId}`, 'GET', 'FAIL', 
          '获取问卷详情失败', detailResponse);
      }
    }
    
    // 测试创建问卷（需要认证）
    if (authToken) {
      const createResponse = await makeRequest(`${BASE_URL}/api/v1/surveys/`, {
        method: 'POST',
        body: JSON.stringify({
          title: `测试问卷 ${Date.now()}`,
          description: '这是一个测试问卷',
          status: 'draft'
        })
      });
      
      if (createResponse.ok || createResponse.status === 201) {
        recordTest('/api/v1/surveys/', 'POST', 'PASS', 
          '创建问卷成功', createResponse.data);
      } else {
        recordTest('/api/v1/surveys/', 'POST', 'FAIL', 
          '创建问卷失败', createResponse);
      }
    }
  } else {
    recordTest('/api/v1/surveys/', 'GET', 'FAIL', 
      '获取问卷列表失败', listResponse);
  }
}

/**
 * 测试7：问题管理
 */
async function testQuestions() {
  console.log('\n📋 测试 7: 问题管理');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/questions/`);
  
  if (response.ok) {
    recordTest('/api/v1/questions/', 'GET', 'PASS', 
      `获取问题列表成功，共 ${response.data?.length || 0} 个问题`, 
      { count: response.data?.length });
  } else {
    recordTest('/api/v1/questions/', 'GET', 'FAIL', 
      '获取问题列表失败', response);
  }
}

/**
 * 测试8：答案管理
 */
async function testAnswers() {
  console.log('\n📋 测试 8: 答案管理');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/answers/`);
  
  if (response.ok) {
    recordTest('/api/v1/answers/', 'GET', 'PASS', 
      `获取答案列表成功，共 ${response.data?.length || 0} 个答案`, 
      { count: response.data?.length });
  } else {
    recordTest('/api/v1/answers/', 'GET', 'FAIL', 
      '获取答案列表失败', response);
  }
}

/**
 * 测试9：部门管理
 */
async function testDepartments() {
  console.log('\n📋 测试 9: 部门管理');
  console.log('='.repeat(60));
  
  // 先获取组织列表
  const orgResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/`);
  
  if (orgResponse.ok && orgResponse.data && orgResponse.data.length > 0) {
    const orgId = orgResponse.data[0].id;
    const deptResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/${orgId}/departments`);
    
    if (deptResponse.ok) {
      recordTest(`/api/v1/organizations/${orgId}/departments`, 'GET', 'PASS', 
        `获取部门列表成功，共 ${deptResponse.data?.length || 0} 个部门`, 
        { count: deptResponse.data?.length });
    } else {
      recordTest(`/api/v1/organizations/${orgId}/departments`, 'GET', 'FAIL', 
        '获取部门列表失败', deptResponse);
    }
  } else {
    recordTest('/api/v1/organizations/{org_id}/departments', 'GET', 'SKIP', 
      '没有可用的组织，跳过部门测试');
  }
}

/**
 * 测试10：参与者管理
 */
async function testParticipants() {
  console.log('\n📋 测试 10: 参与者管理');
  console.log('='.repeat(60));
  
  // 先获取组织列表
  const orgResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/`);
  
  if (orgResponse.ok && orgResponse.data && orgResponse.data.length > 0) {
    const orgId = orgResponse.data[0].id;
    const participantResponse = await makeRequest(`${BASE_URL}/api/v1/organizations/${orgId}/participants`);
    
    if (participantResponse.ok) {
      recordTest(`/api/v1/organizations/${orgId}/participants`, 'GET', 'PASS', 
        `获取参与者列表成功，共 ${participantResponse.data?.length || 0} 个参与者`, 
        { count: participantResponse.data?.length });
    } else {
      recordTest(`/api/v1/organizations/${orgId}/participants`, 'GET', 'FAIL', 
        '获取参与者列表失败', participantResponse);
    }
  } else {
    recordTest('/api/v1/organizations/{org_id}/participants', 'GET', 'SKIP', 
      '没有可用的组织，跳过参与者测试');
  }
}

/**
 * 测试11：分析 API
 */
async function testAnalytics() {
  console.log('\n📋 测试 11: 分析 API');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/analytics/`);
  
  if (response.ok) {
    recordTest('/api/v1/analytics/', 'GET', 'PASS', 
      '分析 API 可用', response.data);
  } else {
    recordTest('/api/v1/analytics/', 'GET', 'FAIL', 
      '分析 API 不可用', response);
  }
}

/**
 * 测试12：标签管理
 */
async function testTags() {
  console.log('\n📋 测试 12: 标签管理');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/tags/`);
  
  if (response.ok) {
    recordTest('/api/v1/tags/', 'GET', 'PASS', 
      `获取标签列表成功，共 ${response.data?.length || 0} 个标签`, 
      { count: response.data?.length });
  } else {
    recordTest('/api/v1/tags/', 'GET', 'FAIL', 
      '获取标签列表失败', response);
  }
}

/**
 * 测试13：分类管理
 */
async function testCategories() {
  console.log('\n📋 测试 13: 分类管理');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/categories/`);
  
  if (response.ok) {
    recordTest('/api/v1/categories/', 'GET', 'PASS', 
      `获取分类列表成功，共 ${response.data?.length || 0} 个分类`, 
      { count: response.data?.length });
  } else {
    recordTest('/api/v1/categories/', 'GET', 'FAIL', 
      '获取分类列表失败', response);
  }
}

/**
 * 测试14：LLM API
 */
async function testLLMAPI() {
  console.log('\n📋 测试 14: LLM API');
  console.log('='.repeat(60));
  
  const response = await makeRequest(`${BASE_URL}/api/v1/llm/status`);
  
  if (response.ok) {
    recordTest('/api/v1/llm/status', 'GET', 'PASS', 
      'LLM API 状态检查成功', response.data);
  } else {
    recordTest('/api/v1/llm/status', 'GET', 'FAIL', 
      'LLM API 状态检查失败', response);
  }
}

/**
 * 使用浏览器访问 /docs 页面并截图
 */
async function testDocsPage() {
  console.log('\n📋 测试 15: API 文档页面 (/docs)');
  console.log('='.repeat(60));
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // 访问 /docs 页面
    await page.goto(DOCS_URL, { waitUntil: 'networkidle' });
    
    // 截图
    await page.screenshot({ 
      path: '.opencode/skills/api-docs-page.png',
      fullPage: true 
    });
    
    // 检查页面标题
    const title = await page.title();
    
    // 检查是否有 Swagger UI
    const hasSwaggerUI = await page.locator('#swagger-ui').count() > 0;
    
    // 获取 API 数量
    const apiCount = await page.locator('.opblock').count();
    
    if (hasSwaggerUI && apiCount > 0) {
      recordTest('/docs', 'GET', 'PASS', 
        `API 文档页面加载成功，共发现 ${apiCount} 个 API 端点`, 
        { title, apiCount, screenshot: 'api-docs-page.png' });
    } else {
      recordTest('/docs', 'GET', 'FAIL', 
        'API 文档页面加载异常', { title, hasSwaggerUI, apiCount });
    }
    
  } catch (error) {
    recordTest('/docs', 'GET', 'FAIL', 
      `访问 API 文档页面失败: ${error.message}`, { error: error.message });
  } finally {
    await browser.close();
  }
}

/**
 * 生成测试报告
 */
function generateReport() {
  console.log('\n' + '='.repeat(60));
  console.log('📊 测试报告');
  console.log('='.repeat(60));
  
  const duration = (new Date() - new Date(testResults.startTime)) / 1000;
  
  console.log(`\n⏱️  总耗时: ${duration.toFixed(2)} 秒`);
  console.log(`📊 总测试数: ${testResults.summary.total}`);
  console.log(`✅ 通过: ${testResults.summary.passed}`);
  console.log(`❌ 失败: ${testResults.summary.failed}`);
  console.log(`⚠️  跳过: ${testResults.summary.skipped}`);
  
  const passRate = (testResults.summary.passed / testResults.summary.total * 100).toFixed(2);
  console.log(`\n📈 通过率: ${passRate}%`);
  
  // 保存详细报告到文件
  testResults.endTime = new Date().toISOString();
  testResults.duration = duration;
  
  const reportPath = '.opencode/skills/api-test-report.json';
  fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));
  console.log(`\n📄 详细报告已保存到: ${reportPath}`);
  
  // 生成 Markdown 报告
  const mdReport = generateMarkdownReport();
  const mdReportPath = '.opencode/skills/api-test-report.md';
  fs.writeFileSync(mdReportPath, mdReport);
  console.log(`📄 Markdown 报告已保存到: ${mdReportPath}`);
}

/**
 * 生成 Markdown 报告
 */
function generateMarkdownReport() {
  let md = `# API 接口测试报告

**生成时间**: ${new Date().toLocaleString('zh-CN')}

## 📊 测试概览

- **总测试数**: ${testResults.summary.total}
- **✅ 通过**: ${testResults.summary.passed}
- **❌ 失败**: ${testResults.summary.failed}
- **⚠️ 跳过**: ${testResults.summary.skipped}
- **📈 通过率**: ${(testResults.summary.passed / testResults.summary.total * 100).toFixed(2)}%
- **⏱️ 耗时**: ${testResults.duration.toFixed(2)} 秒

## 📋 详细测试结果

| 序号 | 端点 | 方法 | 状态 | 消息 | 时间 |
|------|------|------|------|------|------|
`;
  
  testResults.tests.forEach((test, index) => {
    const statusIcon = test.status === 'PASS' ? '✅' : (test.status === 'FAIL' ? '❌' : '⚠️');
    const time = new Date(test.timestamp).toLocaleTimeString('zh-CN');
    md += `| ${index + 1} | \`${test.endpoint}\` | ${test.method} | ${statusIcon} ${test.status} | ${test.message} | ${time} |\n`;
  });
  
  // 添加失败的测试详情
  const failedTests = testResults.tests.filter(t => t.status === 'FAIL');
  if (failedTests.length > 0) {
    md += `\n## ❌ 失败的测试详情\n\n`;
    failedTests.forEach((test, index) => {
      md += `### ${index + 1}. ${test.method} ${test.endpoint}\n\n`;
      md += `- **消息**: ${test.message}\n`;
      md += `- **时间**: ${new Date(test.timestamp).toLocaleString('zh-CN')}\n`;
      if (test.details) {
        md += `- **详情**: \n\`\`\`json\n${JSON.stringify(test.details, null, 2)}\n\`\`\`\n`;
      }
      md += '\n';
    });
  }
  
  md += `\n## 📸 截图\n\n`;
  md += `- [API 文档页面](.opencode/skills/api-docs-page.png)\n`;
  md += `\n## 📝 备注\n\n`;
  md += `- 测试用户: ${testUser.username}\n`;
  md += `- 基础 URL: ${BASE_URL}\n`;
  md += `- 文档 URL: ${DOCS_URL}\n`;
  
  return md;
}

/**
 * 主测试流程
 */
async function runAllTests() {
  console.log('🚀 开始 API 接口自动化测试');
  console.log('='.repeat(60));
  console.log(`📍 基础 URL: ${BASE_URL}`);
  console.log(`📖 文档 URL: ${DOCS_URL}`);
  console.log(`👤 测试用户: ${testUser.username}`);
  console.log('='.repeat(60));
  
  try {
    // 依次执行测试
    await testHealthCheck();
    await testUserRegistration();
    await testUserLogin();
    await testGetCurrentUser();
    await testOrganizations();
    await testSurveys();
    await testQuestions();
    await testAnswers();
    await testDepartments();
    await testParticipants();
    await testAnalytics();
    await testTags();
    await testCategories();
    await testLLMAPI();
    await testDocsPage();
    
    // 生成报告
    generateReport();
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error);
    console.error(error.stack);
  }
}

// 运行测试
runAllTests();
