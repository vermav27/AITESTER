const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const requiredFiles = [
  'index.html',
  'styles.css',
  'src/app.js',
  'api/_workflow-status.js',
  'api/report-bug.js',
  'api/report-status.js',
  'scripts/local-server.js',
  'scripts/should-ignore-build.js',
  'vercel.json',
  'package.json',
];

for (const file of requiredFiles) {
  if (!fs.existsSync(path.join(root, file))) {
    throw new Error(`Missing required file: ${file}`);
  }
}

const browserFiles = [
  fs.readFileSync(path.join(root, 'index.html'), 'utf8'),
  fs.readFileSync(path.join(root, 'styles.css'), 'utf8'),
  fs.readFileSync(path.join(root, 'src/app.js'), 'utf8'),
];

for (const content of browserFiles) {
  if (/n8n|app\.n8n\.cloud|vineetverma\.app\.n8n\.cloud/i.test(content)) {
    throw new Error('Browser-facing files must not mention the automation provider or URL.');
  }
}

console.log('Validation passed. App is Vercel-ready and browser-facing copy is clean.');
