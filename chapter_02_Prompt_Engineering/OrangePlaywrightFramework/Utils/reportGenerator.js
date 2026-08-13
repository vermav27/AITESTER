/**
 * ReportGenerator — a Playwright custom reporter (RICE-POT I-7).
 *
 * Its onEnd() hook runs after all tests finish, collects the results directly
 * from the test run, and writes a colorful HTML report into Reports/ named
 * `TestReport_<DateStamp>_<TimeStamp>.html` containing:
 *   - a colored summary banner (green = approved, red = not approved)
 *   - per-test status rows (green PASS / red FAIL)
 *   - counts of passed / failed / total tests
 *   - the passing percentage
 *   - a 99% pass-rate gate: "APPROVED" at >= 99%, "NOT APPROVED" below
 *
 * After report generation, automatically cleans up old test runs (keeps last 5).
 *
 * The same summary is printed to the console (RICE-POT O-1).
 *
 * Registered in playwright.config.js:
 *   reporter: [ ['list'], ['json', {...}], [ './Utils/reportGenerator' ] ]
 */
const fs = require('fs');
const path = require('path');

const config = require('../config/config');
const { cleanup } = require('./cleanupManager');

function dateStamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`;
}

function timeStamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function buildHtml(results, summary) {
  const { total, passed, failed, passRate, approved, threshold } = summary;
  const rows = results
    .map((r) => {
      const color = r.status === 'PASS' ? '#1a7f37' : '#cf222e';
      const icon = r.status === 'PASS' ? '&#10004;' : '&#10008;';
      const dur = (r.durationMs / 1000).toFixed(2);
      return (
        `<tr style="border-bottom:1px solid #e1e4e8;background:${r.status === 'PASS' ? '#e6ffec' : '#ffebe9'}">
           <td style="padding:10px 16px;color:${color};font-weight:600;">${icon} ${r.status}</td>
           <td style="padding:10px 16px;">${escapeHtml(r.title)}</td>
           <td style="padding:10px 16px;color:#57606a;">${escapeHtml(r.file)}</td>
           <td style="padding:10px 16px;color:#57606a;text-align:right;">${dur}s</td>
         </tr>`
      );
    })
    .join('');

  const bannerBg = approved ? '#dafbe1' : '#ffebe9';
  const bannerColor = approved ? '#1a7f37' : '#cf222e';
  const badge = approved ? 'APPROVED' : 'NOT APPROVED';

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>OrangeHRM Test Report — ${dateStamp()}_${timeStamp()}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f6f8fa; color: #24292f; }
  .container { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; }
  h1 { font-size: 24px; margin: 0 0 4px; }
  .subtitle { color: #57606a; margin-bottom: 24px; }
  .banner { border-radius: 8px; padding: 20px 24px; margin-bottom: 24px; background: ${bannerBg}; border: 2px solid ${bannerColor}; }
  .banner h2 { margin: 0 0 8px; color: ${bannerColor}; }
  .stats { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0 24px; }
  .stat-card { flex: 1; min-width: 140px; background: #fff; border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; text-align: center; }
  .stat-card .value { font-size: 28px; font-weight: 700; }
  .stat-card .label { font-size: 13px; color: #57606a; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; }
  th { text-align: left; padding: 10px 16px; background: #f6f8fa; border-bottom: 2px solid #d0d7de; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #57606a; }
</style>
</head>
<body>
  <div class="container">
    <h1>OrangeHRM Automation Test Report</h1>
    <div class="subtitle">Run: ${dateStamp()}_${timeStamp()} &bull; Framework: OrangePlaywrightFramework</div>

    <div class="banner">
      <h2>${badge} — Pass Rate Gate: ${passRate.toFixed(2)}% (threshold ${threshold}%)</h2>
      <div>Release go-ahead is granted only at a ${threshold}% pass rate.</div>
    </div>

    <div class="stats">
      <div class="stat-card"><div class="value" style="color:#1a7f37;">${passed}</div><div class="label">Passed</div></div>
      <div class="stat-card"><div class="value" style="color:#cf222e;">${failed}</div><div class="label">Failed</div></div>
      <div class="stat-card"><div class="value">${total}</div><div class="label">Total</div></div>
      <div class="stat-card"><div class="value" style="color:${approved ? '#1a7f37' : '#cf222e'};">${passRate.toFixed(2)}%</div><div class="label">Pass Rate</div></div>
    </div>

    <table>
      <thead><tr><th>Status</th><th>Test</th><th>File</th><th style="text-align:right;">Duration</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>
</body>
</html>`;
}

class ReportGeneratorReporter {
  constructor() {
    this.results = [];
  }

  onTestEnd(test, result) {
    this.results.push({
      title: test.title,
      file: test.location.file,
      status: result.status === 'passed' ? 'PASS' : 'FAIL',
      durationMs: result.duration,
    });
  }

  onEnd() {
    const results = this.results;
    const total = results.length;
    const passed = results.filter((r) => r.status === 'PASS').length;
    const failed = total - passed;
    const passRate = total === 0 ? 0 : (passed / total) * 100;
    const threshold = config.passRateThreshold;
    const approved = passRate >= threshold;

    const frameworkRoot = path.resolve(__dirname, '..');
    const reportsDir = path.join(frameworkRoot, config.reportsDir);
    if (!fs.existsSync(reportsDir)) fs.mkdirSync(reportsDir, { recursive: true });
    const reportPath = path.join(reportsDir, `TestReport_${dateStamp()}_${timeStamp()}.html`);
    fs.writeFileSync(reportPath, buildHtml(results, {
      total, passed, failed, passRate, approved, threshold,
    }));

    // Console summary (RICE-POT O-1)
    const line = '='.repeat(70);
    console.log(`\n${line}`);
    console.log('  ORANGEHRM TEST SUMMARY');
    console.log(line);
    console.log(`  Total tests : ${total}`);
    console.log(`  Passed      : ${passed}`);
    console.log(`  Failed      : ${failed}`);
    console.log(`  Pass rate   : ${passRate.toFixed(2)}%  (threshold: ${threshold}%)`);
    console.log(`  Gate status : ${approved ? 'APPROVED — release go-ahead granted' : 'NOT APPROVED — below 99% pass rate'}`);
    console.log(`  Report      : ${reportPath}`);
    console.log(line + '\n');

    // Cleanup: keep only last 5 test runs across Logs, ScreenshotAttachment, and Reports
    cleanup();
  }
}

module.exports = ReportGeneratorReporter;
