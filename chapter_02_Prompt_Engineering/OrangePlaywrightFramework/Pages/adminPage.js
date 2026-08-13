/**
 * AdminPage — Page Object for the OrangeHRM Admin module.
 * Every locator is an XPath string from Selectors/adminPage.js (RICE-POT I-4).
 */
const AdminSelectors = require('../Selectors/adminPage');

class AdminPage {
  constructor(page) {
    this.page = page;
  }

  async isAdminHeaderVisible() {
    return this.page.locator(AdminSelectors.adminHeader).isVisible();
  }

  async searchUserByUsername(username) {
    await this.page.fill(AdminSelectors.searchUsernameInput, username);
    await this.page.click(AdminSelectors.searchButton);
  }

  async getResultCount() {
    const rows = this.page.locator(AdminSelectors.resultRows);
    await rows.first().waitFor({ state: 'attached', timeout: 10000 }).catch(() => {});
    return rows.count();
  }

  async getResultRowTexts() {
    const cells = this.page.locator(AdminSelectors.resultRowCells);
    return cells.allTextContents();
  }
}

module.exports = AdminPage;
