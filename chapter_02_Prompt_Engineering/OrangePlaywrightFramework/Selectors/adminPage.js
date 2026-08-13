/**
 * adminPage.js — XPath-only selectors for the Admin module (RICE-POT I-4).
 * Used by Pages/adminPage.js and Tests/admin/*.js.
 */
const AdminPage = {
  // Admin section header
  adminHeader: "//h6[text()='Admin']",
  dashboardHeading: "//h6[text()='Dashboard']",
  adminMenuLink: "//a[contains(@class,'oxd-main-menu-item') and .//span[text()='Admin']]",

  // User Management search form
  searchUsernameInput:
    "//label[text()='Username']/ancestor::div[contains(@class,'oxd-input-group')]//input",
  searchRoleDropdown:
    "//label[text()='User Role']/ancestor::div[contains(@class,'oxd-input-group')]//div[contains(@class,'oxd-select-text')]",
  searchEmployeeNameInput:
    "//label[text()='Employee Name']/ancestor::div[contains(@class,'oxd-input-group')]//input",
  searchStatusDropdown:
    "//label[text()='Status']/ancestor::div[contains(@class,'oxd-input-group')]//div[contains(@class,'oxd-select-text')]",
  searchButton: "//button[@type='submit']",
  resetButton: "//button[normalize-space()='Reset']",

  // Results table
  resultRows:
    "//div[contains(@class,'oxd-table-body')]//div[contains(@class,'oxd-table-card')]",
  resultRowCells:
    "//div[contains(@class,'oxd-table-body')]//div[contains(@class,'oxd-table-card')]//div[contains(@class,'oxd-table-cell')]",
  noRecordsFound:
    "//div[contains(@class,'oxd-table-body')]//span[text()='No Records Found']",
};

module.exports = AdminPage;
