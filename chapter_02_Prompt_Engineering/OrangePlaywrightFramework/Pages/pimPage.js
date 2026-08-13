/**
 * PimPage — Page Object for the OrangeHRM PIM module.
 * Every locator is an XPath string from Selectors/pimPage.js (RICE-POT I-4).
 */
const PimSelectors = require('../Selectors/pimPage');

class PimPage {
  constructor(page) {
    this.page = page;
  }

  async isPimHeaderVisible() {
    return this.page.locator(PimSelectors.pimHeader).isVisible();
  }

  async searchEmployeeByName(employeeName) {
    await this.page.fill(PimSelectors.searchEmployeeNameInput, employeeName);
    await this.page.click(PimSelectors.searchButton);
  }

  async getResultCount() {
    const rows = this.page.locator(PimSelectors.resultRows);
    await rows.first().waitFor({ state: 'attached', timeout: 10000 }).catch(() => {});
    return rows.count();
  }

  async getResultRowTexts() {
    const cells = this.page.locator(PimSelectors.resultRowCells);
    return cells.allTextContents();
  }
}

module.exports = PimPage;
