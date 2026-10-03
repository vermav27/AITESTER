const { execSync } = require('node:child_process');

const watchedFile = 'chapter_08_n8n_Agents/05_ScreenshotToBugReporter.json';
const branch = process.env.VERCEL_GIT_COMMIT_REF || '';

function run(command) {
  return execSync(command, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  }).trim();
}

function listChangedFiles() {
  if (process.env.MOCK_CHANGED_FILES) {
    return process.env.MOCK_CHANGED_FILES.split(',').map((file) => file.trim()).filter(Boolean);
  }

  const previousSha = process.env.VERCEL_GIT_PREVIOUS_SHA || '';
  const commitSha = process.env.VERCEL_GIT_COMMIT_SHA || 'HEAD';

  if (previousSha && !/^0+$/.test(previousSha)) {
    return run(`git diff --name-only ${previousSha} ${commitSha}`).split('\n').filter(Boolean);
  }

  try {
    return run('git diff --name-only HEAD~1 HEAD').split('\n').filter(Boolean);
  } catch {
    return run(`git show --pretty="" --name-only ${commitSha}`).split('\n').filter(Boolean);
  }
}

try {
  if (branch !== 'main') {
    console.log(`Ignoring deployment: branch is "${branch || 'unknown'}", not "main".`);
    process.exit(0);
  }

  const changedFiles = listChangedFiles();
  const shouldDeploy = changedFiles.includes(watchedFile);

  if (!shouldDeploy) {
    console.log(`Ignoring deployment: ${watchedFile} did not change.`);
    console.log(`Changed files: ${changedFiles.join(', ') || 'none detected'}`);
    process.exit(0);
  }

  console.log(`Proceeding with deployment: ${watchedFile} changed on main.`);
  process.exit(1);
} catch (error) {
  console.log('Proceeding with deployment: unable to evaluate changed files safely.');
  console.log(error.message);
  process.exit(1);
}
