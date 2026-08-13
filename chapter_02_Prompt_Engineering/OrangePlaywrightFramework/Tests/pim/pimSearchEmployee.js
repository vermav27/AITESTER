/**
 * pimSearchEmployee.js
 * PIM module: log in, open PIM, search for an existing employee, expect results.
 */
const { test, expect } = require('../../Base/baseTest');
const config = require('../../config/config');
const PimPage = require('../../Pages/pimPage');
const PimSelectors = require('../../Selectors/pimPage');

test('Verify PIM employee search returns results for existing employee', async ({ baseTest }) => {
  const pimPage = new PimPage(baseTest.page);

  await baseTest.login(config.validUsername, config.validPassword);
  await baseTest.waitForElementVisible(PimSelectors.dashboardHeading);

  // Navigate to PIM via sidebar
  await baseTest.clickByXPath(PimSelectors.pimMenuLink);
  await baseTest.waitForElementVisible(PimSelectors.pimHeader);
  expect(await pimPage.isPimHeaderVisible()).toBe(true);

  // Search for the logged-in employee "John Smith" (seen in the dashboard screenshot)
  await pimPage.searchEmployeeByName('John Smith');
  const count = await pimPage.getResultCount();
  expect(count).toBeGreaterThan(0);
});
