/**
 * loginUsingInvalidCredential.js
 * RICE-POT E-2: Verify login with invalid credentials shows an error message.
 */
const { test, expect } = require('../../Base/baseTest');
const config = require('../../config/config');
const LoginPage = require('../../Pages/loginPage');
const BaseSelectors = require('../../Selectors/basePage');

test('Verify login with invalid credentials and get error message', async ({ baseTest }) => {
  const loginPage = new LoginPage(baseTest.page);
  await baseTest.login(config.invalidUsername, config.invalidPassword);

  await baseTest.waitForElementVisible(BaseSelectors.invalidCredentialAlert);
  expect(await loginPage.isErrorMessageVisible()).toBe(true);
});
