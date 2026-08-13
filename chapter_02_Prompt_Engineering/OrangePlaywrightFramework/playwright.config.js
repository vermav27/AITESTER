/**
 * Playwright runner configuration for OrangePlaywrightFramework.
 *
 * - Runs all tests under Tests/ (each file = one test) — RICE-POT I-3
 * - Fully parallel execution with 4 workers (headless) — RICE-POT I-11 (parallel runs)
 * - Single worker in headed mode (--headed) to avoid browser conflicts
 * - Single test runs via CLI: npx playwright test <path> — RICE-POT I-11
 * - JSON report feeds Utils/reportGenerator.js (globalTeardown) — RICE-POT I-7
 * - Screenshots are handled by Utils/screenshotManager.js (custom naming) — RICE-POT I-5
 */
const { defineConfig } = require('@playwright/test');

// Detect headed mode from command line args
const isHeaded = process.argv.includes('--headed');

module.exports = defineConfig({
  testDir: './Tests',
  testMatch: '**/*.js',
  fullyParallel: isHeaded ? false : true,  // No parallel in headed mode
  workers: isHeaded ? 1 : 4,  // 1 worker in headed mode, 4 in headless
  retries: isHeaded ? 0 : 2,  // No retries in headed mode (for debugging), 2 in headless
  timeout: 60000,
  expect: { timeout: 15000 },

  reporter: [
    ['list'],
    ['json', { outputFile: 'test-results/test-results.json' }],
    // Custom reporter: colored HTML report + 99% pass-rate gate (RICE-POT I-7)
    ['./Utils/reportGenerator.js'],
  ],

  use: {
    baseURL: 'https://opensource-demo.orangehrmlive.com/',
    headless: !isHeaded,
    viewport: { width: 1440, height: 900 },
    screenshot: 'off', // custom screenshot manager owns naming (RICE-POT I-5)
    trace: 'retain-on-failure',
  },

  webServer: undefined,

  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        launchArgs: [
          // Disable sandbox for headed mode (macOS socket directory fix)
          ...(isHeaded ? ['--single-process', '--no-zygote'] : []),
        ],
      },
    },
  ],
});
