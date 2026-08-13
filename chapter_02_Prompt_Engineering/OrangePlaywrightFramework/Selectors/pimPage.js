/**
 * pimPage.js — XPath-only selectors for the PIM module (RICE-POT I-4).
 * Used by Pages/pimPage.js and Tests/pim/*.js.
 */
const PimPage = {
  // PIM section header
  pimHeader: "//h6[text()='PIM']",
  dashboardHeading: "//h6[text()='Dashboard']",
  pimMenuLink: "//a[contains(@class,'oxd-main-menu-item') and .//span[text()='PIM']]",

  // Employee Information search form
  searchEmployeeNameInput:
    "//label[text()='Employee Name']/ancestor::div[contains(@class,'oxd-input-group')]//input",
  searchIdInput:
    "//label[text()='Employee Id']/ancestor::div[contains(@class,'oxd-input-group')]//input",
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

module.exports = PimPage;
