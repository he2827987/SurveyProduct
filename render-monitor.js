const API_KEY = 'rnd_F0BAVRpEboOXEm2WM8HlS8HS8cc6';
const SERVICE_ID = 'srv-d379sp8gjchc73c3ju9g';
const SERVICE_URL = 'https://surveyproduct.onrender.com';

async function check() {
  const res = await fetch(`https://api.render.com/v1/services/${SERVICE_ID}/deploys?limit=1`, {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
  const data = await res.json();
  return data[0]?.deploy;
}

(async () => {
  console.log('Monitoring deploy...\n');
  const start = Date.now();
  let lastStatus = '';

  while (Date.now() - start < 15 * 60 * 1000) {
    const deploy = await check();
    if (!deploy) { await new Promise(r => setTimeout(r, 15000)); continue; }

    const elapsed = Math.round((Date.now() - start) / 1000);
    const status = deploy.status;

    if (status !== lastStatus) {
      console.log(`[${elapsed}s] ${status} | commit: ${deploy.commit?.id?.substring(0, 8)} | trigger: ${deploy.trigger}`);
      lastStatus = status;
    } else {
      process.stdout.write('.');
    }

    if (status === 'live') {
      console.log('\n\nDEPLOY SUCCESSFUL!');
      console.log('URL:', SERVICE_URL);
      const health = await fetch(SERVICE_URL, { signal: AbortSignal.timeout(10000) }).catch(e => ({ error: e.message }));
      if (health.status) console.log('HTTP Status:', health.status);
      else console.log('Health check error:', health.error);
      process.exit(0);
    }

    if (['update_failed', 'build_failed', 'canceled'].includes(status)) {
      console.log(`\n\nDEPLOY FAILED: ${status}`);
      console.log('Commit:', deploy.commit?.message);
      console.log('Finished:', deploy.finishedAt);
      process.exit(1);
    }

    await new Promise(r => setTimeout(r, 15000));
  }

  console.log('\nTimeout');
  process.exit(1);
})();
