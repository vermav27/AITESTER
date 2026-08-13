/**
 * LoginPage — Page Object for the OrangeHRM login screen.
 * Every locator is an XPath string from Selectors/basePage.js (RICE-POT I-4).
 */
const BaseSelectors = require('../Selectors/basePage');

class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async navigate() {
    await this.page.goto('/');
  }

  async enterUsername(username) {
    await this.page.fill(BaseSelectors.usernameInput, username);
  }

  async enterPassword(password) {
    await this.page.fill(BaseSelectors.passwordInput, password);
  }

  async clickLogin() {
    await this.page.click(BaseSelectors.loginButton);
  }

  async login(username, password) {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLogin();
  }

  async getErrorMessage() {
    const alert = this.page.locator(BaseSelectors.invalidCredentialAlert);
    await alert.waitFor({ state: 'visible', timeout: 10000 });
    return (await alert.textContent()).trim();
  }

  async isErrorMessageVisible() {
    return this.page.locator(BaseSelectors.invalidCredentialAlert).isVisible();
  }

  async isLoginButtonVisible() {
    return this.page.locator(BaseSelectors.loginButton).isVisible();
  }
}

module.exports = LoginPage;
