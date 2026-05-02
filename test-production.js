const PROD_URL = 'https://surveyproduct.onrender.com';

let passed = 0, failed = 0, errors = [];
let token = '';

function log(msg) { console.log(msg); }

async function api(method, path, body = null, useAuth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (useAuth && token) headers['Authorization'] = `Bearer ${token}`;
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${PROD_URL}${path}`, opts);
  let data;
  try { data = await res.json(); } catch { data = await res.text(); }
  return { status: res.status, data };
}

async function test(name, fn) {
  try {
    await fn();
    passed++;
    log(`  PASS: ${name}`);
  } catch (e) {
    failed++;
    errors.push({ test: name, error: e.message });
    log(`  FAIL: ${name} - ${e.message}`);
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message || 'Assertion failed');
}

(async () => {
  log('\n========================================');
  log(`  Production API Test Suite`);
  log(`  Target: ${PROD_URL}`);
  log(`  Time: ${new Date().toISOString()}`);
  log('========================================\n');

  // ===== 1. Basic Connectivity =====
  log('--- 1. Basic Connectivity ---');
  await test('GET / returns API running message', async () => {
    const { status, data } = await api('GET', '/');
    assert(status === 200, `Expected 200, got ${status}`);
    assert(data.message === 'Survey API is running', `Unexpected: ${JSON.stringify(data)}`);
  });

  await test('GET /docs returns Swagger UI', async () => {
    const res = await fetch(`${PROD_URL}/docs`);
    assert(res.status === 200, `Expected 200, got ${res.status}`);
    const text = await res.text();
    assert(text.includes('swagger') || text.includes('Swagger'), 'Not Swagger UI');
  });

  await test('GET /test returns test message', async () => {
    const res = await fetch(`${PROD_URL}/test`);
    const data = await res.json();
    assert(res.status === 200, `Expected 200, got ${res.status}`);
    assert(data.message === 'Test endpoint working!', `Unexpected: ${JSON.stringify(data)}`);
  });

  // ===== 2. Authentication =====
  log('\n--- 2. Authentication ---');
  const LOGIN_URL = '/api/v1/users/login/access-token';
  const TEST_EMAIL = 'he2827987@gmail.com';
  const TEST_PASS = '13245678';

  await test('POST /api/v1/users/register - register test user', async () => {
    const { status, data } = await api('POST', '/api/v1/users/register', {
      email: TEST_EMAIL,
      password: TEST_PASS,
      username: 'testuser'
    });
    assert(status === 200 || status === 201 || status === 400, `Register: ${status} ${JSON.stringify(data)}`);
    if (status === 400) log(`    User already exists (expected)`);
    else log(`    User registered: ${JSON.stringify(data)}`);
  });

  await test('POST /api/v1/users/login/access-token - login', async () => {
    const formBody = `username=${encodeURIComponent(TEST_EMAIL)}&password=${encodeURIComponent(TEST_PASS)}`;
    const res = await fetch(`${PROD_URL}${LOGIN_URL}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formBody
    });
    const data = await res.json();
    assert(res.status === 200, `Login failed: ${res.status} ${JSON.stringify(data)}`);
    assert(data.access_token, 'No access_token in response');
    token = data.access_token;
    log(`    Token obtained: ${token.substring(0, 20)}...`);
  });

  await test('GET /api/v1/users/me - get current user', async () => {
    const { status, data } = await api('GET', '/api/v1/users/me', null, true);
    assert(status === 200, `Expected 200, got ${status}: ${JSON.stringify(data)}`);
    assert(data.email === 'he2827987@gmail.com', `Unexpected user: ${JSON.stringify(data)}`);
    log(`    User: ${data.email} (id: ${data.id})`);
  });

  await test('Login with invalid credentials returns error', async () => {
    const formBody = `username=invalid@test.com&password=wrongpass`;
    const res = await fetch(`${PROD_URL}${LOGIN_URL}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formBody
    });
    assert(res.status === 401, `Expected 401, got ${res.status}`);
  });

  // ===== 3. Survey CRUD =====
  log('\n--- 3. Survey CRUD ---');
  let surveyId;

  await test('GET /api/v1/surveys/ - list surveys', async () => {
    const { status, data } = await api('GET', '/api/v1/surveys/', null, true);
    assert(status === 200, `Expected 200, got ${status}: ${JSON.stringify(data)}`);
    const surveys = Array.isArray(data) ? data : (data.items || []);
    log(`    Found ${surveys.length} surveys`);
  });

  await test('POST /api/v1/surveys/ - create survey', async () => {
    const { status, data } = await api('POST', '/api/v1/surveys/', {
      title: `线上测试问卷 - ${Date.now()}`,
      description: '自动化线上测试创建的问卷'
    }, true);
    assert(status === 200 || status === 201, `Expected 200/201, got ${status}: ${JSON.stringify(data)}`);
    assert(data.id, 'No survey id returned');
    surveyId = data.id;
    log(`    Created survey id: ${surveyId}`);
  });

  await test('GET /api/v1/surveys/{id} - get survey detail', async () => {
    const { status, data } = await api('GET', `/api/v1/surveys/${surveyId}`, null, true);
    assert(status === 200, `Expected 200, got ${status}: ${JSON.stringify(data)}`);
    assert(data.id === surveyId, `ID mismatch: ${data.id} vs ${surveyId}`);
  });

  await test('PUT /api/v1/surveys/{id} - update survey', async () => {
    const { status, data } = await api('PUT', `/api/v1/surveys/${surveyId}`, {
      title: `线上测试问卷(已更新) - ${Date.now()}`,
      description: '更新后的描述'
    }, true);
    assert(status === 200, `Expected 200, got ${status}: ${JSON.stringify(data)}`);
  });

  // ===== 4. Question CRUD =====
  log('\n--- 4. Question CRUD ---');
  let questionId;

  await test('POST /api/v1/questions/ - create question', async () => {
    const { status, data } = await api('POST', '/api/v1/questions/', {
      survey_id: surveyId,
      text: '线上测试题目 - 您对产品满意吗？',
      type: 'single_choice',
      options: ['非常满意', '满意', '一般', '不满意'],
      order: 1
    }, true);
    assert(status === 200 || status === 201, `Expected 200/201, got ${status}: ${JSON.stringify(data)}`);
    questionId = data.id;
    log(`    Created question id: ${questionId}`);
  });

  await test('GET /api/v1/questions/?survey_id={id} - list questions', async () => {
    const { status, data } = await api('GET', `/api/v1/questions/?survey_id=${surveyId}`, null, true);
    assert(status === 200, `Expected 200, got ${status}: ${JSON.stringify(data)}`);
    const questions = Array.isArray(data) ? data : (data.items || []);
    log(`    Found ${questions.length} questions`);
  });

  // ===== 5. Survey Response / Answer =====
  log('\n--- 5. Survey Responses ---');
  await test(`POST /api/v1/surveys/${surveyId}/answers/ - submit answer`, async () => {
    const { status, data } = await api('POST', `/api/v1/surveys/${surveyId}/answers/`, {
      answers: { [questionId]: '满意' }
    }, true);
    assert(status === 200 || status === 201, `Expected 200/201, got ${status}: ${JSON.stringify(data)}`);
  });

  await test(`GET /api/v1/surveys/${surveyId}/answers/ - get answers`, async () => {
    const res = await fetch(`${PROD_URL}/api/v1/surveys/${surveyId}/answers/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    assert(res.status === 200, `Expected 200, got ${res.status}`);
    const data = await res.json();
    log(`    Answers: ${JSON.stringify(data).substring(0, 200)}`);
  });

  // ===== 6. Analytics =====
  log('\n--- 6. Analytics ---');
  await test('GET /api/v1/analytics/survey/{id}/pie - pie chart data', async () => {
    const { status } = await api('GET', `/api/v1/analytics/survey/${surveyId}/pie`, null, true);
    assert(status === 200 || status === 404, `Unexpected status: ${status}`);
  });

  await test('GET /api/v1/analysis/survey/{id} - analysis data', async () => {
    const { status } = await api('GET', `/api/v1/analysis/survey/${surveyId}`, null, true);
    assert(status === 200 || status === 404, `Unexpected status: ${status}`);
  });

  // ===== 7. Department & Organization =====
  log('\n--- 7. Department & Organization ---');
  await test('GET /api/v1/departments/ - list departments', async () => {
    const { status } = await api('GET', '/api/v1/departments/', null, true);
    assert(status === 200 || status === 404, `Unexpected status: ${status}`);
  });

  await test('GET /api/v1/organizations/ - list organizations', async () => {
    const { status } = await api('GET', '/api/v1/organizations/', null, true);
    assert(status === 200 || status === 404, `Unexpected status: ${status}`);
  });

  // ===== 8. Auth Protection =====
  log('\n--- 8. Auth Protection ---');
  await test('Unauthenticated request to protected endpoint returns 401', async () => {
    const { status } = await api('GET', '/api/v1/surveys/');
    assert(status === 401, `Expected 401, got ${status}`);
  });

  // ===== 9. Cleanup =====
  log('\n--- 9. Cleanup ---');
  await test('DELETE /api/v1/surveys/{id} - delete test survey', async () => {
    const { status } = await api('DELETE', `/api/v1/surveys/${surveyId}`, null, true);
    assert(status === 200 || status === 204, `Expected 200/204, got ${status}`);
  });

  // ===== Summary =====
  log('\n========================================');
  log(`  Test Results: ${passed} passed, ${failed} failed`);
  log('========================================');
  if (errors.length > 0) {
    log('\nFailed tests:');
    errors.forEach(e => log(`  - ${e.test}: ${e.error}`));
  }
  log(`\nTotal: ${passed + failed} tests`);

  process.exit(failed > 0 ? 1 : 0);
})();
