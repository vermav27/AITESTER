/**
 * ScreenshotManager — creates a per-run folder under ScreenshotAttachment/
 * named `TestRun_<DateStamp>_<TimeStamp>` (RICE-POT I-5) and captures
 * screenshots named:
 *   Passed : <TestName>_PASS_<DateStamp>_<TimeStamp>.png
 *   Failed : <TestName>_FAIL_<DateStamp>_<TimeStamp>.png
 *
 * The ScreenshotAttachment/ folder is gitignored.
 */
const fs = require('fs');
const path = require('path');

const config = require('../config/config');

let runDir = null;

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

/**
 * Creates the per-run screenshot folder once (thread-safe via lazy init).
 * Returns the absolute path of the run folder.
 */
function initRun() {
  if (runDir) return runDir;
  const frameworkRoot = path.resolve(__dirname, '..');
  const root = path.join(frameworkRoot, config.screenshotDir);
  if (!fs.existsSync(root)) fs.mkdirSync(root, { recursive: true });
  runDir = path.join(root, `TestRun_${dateStamp()}_${timeStamp()}`);
  if (!fs.existsSync(runDir)) fs.mkdirSync(runDir, { recursive: true });
  return runDir;
}

/**
 * Captures a screenshot for a test.
 * @param {import('playwright').Page} page
 * @param {string} testName - test title (used as file base name)
 * @param {'PASS'|'FAIL'} status
 * @returns {Promise<string|null>} absolute path of saved screenshot, or null on failure
 */
async function capture(page, testName, status) {
  try {
    const dir = initRun();
    const safeName = testName.replace(/[^a-zA-Z0-9_-]/g, '_');
    const fileName = `${safeName}_${status}_${dateStamp()}_${timeStamp()}.png`;
    const filePath = path.join(dir, fileName);
    await page.screenshot({ path: filePath, fullPage: true });
    return filePath;
  } catch (err) {
    console.error(`[ScreenshotManager] Failed to capture screenshot: ${err.message}`);
    return null;
  }
}

module.exports = { initRun, capture, getRunDir: () => runDir };
