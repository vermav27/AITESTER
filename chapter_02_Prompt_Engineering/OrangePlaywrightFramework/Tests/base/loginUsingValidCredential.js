/**
 * loginUsingValidCredential.js
 * RICE-POT E-1: Verify login with valid credentials and land on the dashboard.
 */
const { test, expect } = require('../../Base/baseTest');
const config = require('../../config/config');
const BaseSelectors = require('../../Selectors/basePage');

test('Verify login with valid credentials and lands on dashboard', async ({ baseTest }) => {
  await baseTest.login(config.validUsername, config.validPassword);

  // Stable subset: dashboard heading + sidebar visible (not URL-dependent).
  await baseTest.waitForElementVisible(BaseSelectors.dashboardHeading);
  expect(await baseTest.isDashboardVisible()).toBe(true);
  expect(await baseTest.page.url()).toContain('/dashboard');
});
