/**
 * adminSearchUser.js
 * Admin module: log in, open Admin, search for an existing user, expect results.
 */
const { test, expect } = require('../../Base/baseTest');
const config = require('../../config/config');
const AdminPage = require('../../Pages/adminPage');
const AdminSelectors = require('../../Selectors/adminPage');

test('Verify Admin user search returns results for existing user', async ({ baseTest }) => {
  const adminPage = new AdminPage(baseTest.page);

  await baseTest.login(config.validUsername, config.validPassword);
  await baseTest.waitForElementVisible(AdminSelectors.dashboardHeading);

  // Navigate to Admin via sidebar
  await baseTest.clickByXPath(AdminSelectors.adminMenuLink);
  await baseTest.waitForElementVisible(AdminSelectors.adminHeader);
  expect(await adminPage.isAdminHeaderVisible()).toBe(true);

  // Search for the existing "Admin" user
  await adminPage.searchUserByUsername(config.validUsername);
  const count = await adminPage.getResultCount();
  expect(count).toBeGreaterThan(0);
});
