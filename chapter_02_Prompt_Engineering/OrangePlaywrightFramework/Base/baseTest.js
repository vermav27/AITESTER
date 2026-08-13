/**
 * baseTest.js — the common base for every test in the framework (RICE-POT I-3).
 *
 * A custom @playwright/test fixture that runs on EVERY test:
 *   Setup   : initializes the per-run Logs file + ScreenshotAttachment folder,
 *             opens the base URL (single QA environment — RICE-POT I-8).
 *   Helpers : login / logout / waitForElementVisible / waitForElementInvisible
 *             / clickByXPath / fillByXPath — all XPath-based (RICE-POT I-4).
 *   Teardown: logs the test outcome and captures a PASS/FAIL screenshot with
 *             the naming convention
 *             <TestName>_PASS|FAIL_<DateStamp>_<TimeStamp>.png (RICE-POT I-5).
 *
 * Test files import { test, expect } from this module and use the fixture:
 *   test('...', async ({ baseTest }) => { ... });
 */
const { test, expect } = require('@playwright/test');

const config = require('../config/config');
const logger = require('../Utils/logger');
const screenshotManager = require('../Utils/screenshotManager');
const LoginPage = require('../Pages/loginPage');
const BaseSelectors = require('../Selectors/basePage');

// ---------------------------------------------------------------------------
// Shared helper object attached to the fixture. Methods use XPath only.
// ---------------------------------------------------------------------------
const helpers = {
  async login(page, username, password) {
    const loginPage = new LoginPage(page);
    logger.info(`Logging in with user: ${username}`);
    await loginPage.login(username, password);
  },

  async logout(page) {
    logger.info('Logging out');
    await page.click(BaseSelectors.userDropdown);
    await page.click(BaseSelectors.logoutOption);
    await page.waitForURL(/login/i, { timeout: 15000 });
    logger.info('Logout successful');
  },

  async waitForElementVisible(page, xpath, timeout = 15000) {
    await page.locator(xpath).first().waitFor({ state: 'visible', timeout });
  },

  async waitForElementInvisible(page, xpath, timeout = 15000) {
    await page.locator(xpath).first().waitFor({ state: 'hidden', timeout });
  },

  async clickByXPath(page, xpath) {
    await page.locator(xpath).first().click();
  },

  async fillByXPath(page, xpath, value) {
    await page.locator(xpath).first().fill(value);
  },

  async isDashboardVisible(page) {
    return page.locator(BaseSelectors.dashboardHeading).isVisible();
  },
};

// ---------------------------------------------------------------------------
// Custom fixture. Setup runs before each test, teardown after each test.
// ---------------------------------------------------------------------------
const baseTest = test.extend({
  baseTest: async ({ page }, use, testInfo) => {
    // ---- Setup: per-run log file + screenshot run folder + base URL ----
    logger.init();
    screenshotManager.initRun();
    logger.info(`TEST START: ${testInfo.title}`);
    logger.info(`Opening base URL: ${config.baseURL}`);
    await page.goto(config.baseURL);
    // Wait for the login form to be ready before any test starts typing.
    await page.locator(BaseSelectors.usernameInput).first().waitFor({
      state: 'visible',
      timeout: 30000,
    });

    // ---- Expose helpers to the test body ----
    await use({
      login: (username, password) => helpers.login(page, username, password),
      logout: () => helpers.logout(page),
      waitForElementVisible: (xpath, timeout) =>
        helpers.waitForElementVisible(page, xpath, timeout),
      waitForElementInvisible: (xpath, timeout) =>
        helpers.waitForElementInvisible(page, xpath, timeout),
      clickByXPath: (xpath) => helpers.clickByXPath(page, xpath),
      fillByXPath: (xpath, value) => helpers.fillByXPath(page, xpath, value),
      isDashboardVisible: () => helpers.isDashboardVisible(page),
      page,
    });

    // ---- Teardown: log outcome + PASS/FAIL screenshot (RICE-POT I-5) ----
    const status = testInfo.status === 'passed' ? 'PASS' : 'FAIL';
    logger.info(`TEST ${status === 'PASS' ? 'PASSED' : 'FAILED'}: ${testInfo.title}`);
    const shotPath = await screenshotManager.capture(page, testInfo.title, status);
    logger.info(`Screenshot saved: ${shotPath}`);
    if (status === 'FAIL') {
      logger.error(`Failure details: ${testInfo.error ? testInfo.error.message : 'see trace'}`);
    }
  },
});

module.exports = { test: baseTest, expect };
