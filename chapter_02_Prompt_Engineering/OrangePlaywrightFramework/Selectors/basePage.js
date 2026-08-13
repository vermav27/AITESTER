/**
 * basePage.js — XPath-only selectors for the elements used by Base/baseTest.js
 * (login form, logout, dashboard, wait-for helpers). RICE-POT I-4: ONLY XPath
 * locators are allowed anywhere in the framework.
 */
const BasePage = {
  // ---- Login form ----
  usernameInput: "//input[@placeholder='Username']",
  passwordInput: "//input[@placeholder='Password']",
  loginButton: "//button[@type='submit']",
  invalidCredentialAlert: "//p[contains(@class,'oxd-alert-content-text')]",
  forgotPasswordLink: "//a[text()='Forgot your password?']",

  // ---- Logout ----
  userDropdown: "//span[contains(@class,'oxd-userdropdown-tab')]",
  logoutOption: "//a[text()='Logout']",

  // ---- Dashboard (post-login landing) ----
  dashboardHeading: "//h6[text()='Dashboard']",

  // ---- Sidebar navigation ----
  adminMenuLink: "//a[contains(@class,'oxd-main-menu-item') and .//span[text()='Admin']]",
  pimMenuLink: "//a[contains(@class,'oxd-main-menu-item') and .//span[text()='PIM']]",
  dashboardMenuLink: "//a[contains(@class,'oxd-main-menu-item') and .//span[text()='Dashboard']]",
};

module.exports = BasePage;
