# OrangePlaywrightFramework

Enterprise-level **JavaScript / Playwright** automation framework for **OrangeHRM**, built on the **Page Object Model (POM)** with **XPath-only locators**. Every run produces timestamped screenshots, logs, and a colored HTML report with a **99% pass-rate gate**.

---

## Architecture

```
                        ┌──────────────────────────────────────────────┐
                        │            playwright.config.js             │
                        │  (parallel workers · retries · reporters)   │
                        └──────────────────────┬───────────────────────┘
                                               │ loads
                        ┌──────────────────────▼───────────────────────┐
                        │               config/config.js               │
                        │   baseURL · valid/invalid credentials · gate │
                        └──────────────────────┬───────────────────────┘
                                               │
   ┌───────────────────────────┐               │                ┌───────────────────────────┐
   │        Tests/             │  import test  │                │         Utils/            │
   │  base/  · admin/ · pim/   │──────────────►│◄───────────────│  logger · screenshotMgr   │
   │  (one test per file)      │  + expect     │                │  reportGenerator         │
   └───────────┬───────────────┘               │                └─────────────┬─────────────┘
               │ use helper fixture            │                              │
   ┌───────────▼───────────────┐               │                ┌─────────────▼─────────────┐
   │      Base/baseTest.js     │  extends      │                │      Run Artifacts        │
   │  setup · login/logout ·   │  Playwright   │                │  ScreenshotAttachment/    │
   │  wait/click/fill helpers  │  test         │                │  Logs/ · Reports/         │
   └───────────┬───────────────┘               │                └───────────────────────────┘
               │ instantiate page objects      │
   ┌───────────▼───────────────┐   ┌───────────▼───────────────┐
   │        Pages/ (POM)       │   │      Selectors/           │
   │  LoginPage · AdminPage    │──►│  basePage · adminPage     │
   │  PimPage                  │   │  pimPage (XPath ONLY)     │
   └───────────────────────────┘   └───────────────────────────┘
```

**Flow:** `Tests` → `Base/baseTest.js` (fixture: setup + helpers) → `Pages/` (POM) → `Selectors/` (XPath) → OrangeHRM. The fixture also drives `Utils/` (logger + screenshots) and Playwright's `globalTeardown` produces the report.

---

## Folder Structure

```
OrangePlaywrightFramework/
├── package.json                  # scripts: test, test:headed, test:single, test:report
├── playwright.config.js          # parallel (4 workers headless), serial (1 worker headed), retries, reporters
├── .env.example                  # template — copy to .env to override credentials
├── .gitignore                    # ignores node_modules, artifacts, .env
├── config/
│   └── config.js                 # baseURL + credentials + pass-rate threshold (single QA env)
├── Base/
│   └── baseTest.js               # custom fixture: setup, login/logout, wait helpers, screenshots
├── Selectors/
│   ├── basePage.js               # XPath selectors for login/logout/dashboard/sidebar
│   ├── adminPage.js              # XPath selectors for the Admin module
│   └── pimPage.js                # XPath selectors for the PIM module
├── Pages/
│   ├── loginPage.js              # POM — login screen
│   ├── adminPage.js              # POM — Admin module
│   └── pimPage.js                # POM — PIM module
├── Tests/
│   ├── base/
│   │   ├── loginUsingValidCredential.js
│   │   └── loginUsingInvalidCredential.js
│   ├── admin/
│   │   └── adminSearchUser.js
│   └── pim/
│       └── pimSearchEmployee.js
├── Utils/
│   ├── logger.js                 # Logs/Logs_TestRun_<DateStamp>_<TimeStamp>.txt + console
│   ├── screenshotManager.js      # ScreenshotAttachment/TestRun_<DateStamp>_<TimeStamp>/
│   ├── reportGenerator.js        # Reports/TestReport_<DateStamp>_<TimeStamp>.html + 99% gate
│   └── cleanupManager.js         # Automatic cleanup: keeps only last 5 test runs
├── ScreenshotAttachment/         # (generated, gitignored) run folders + PASS/FAIL screenshots
├── Logs/                         # (generated, gitignored) per-run log files
└── Reports/                      # (generated, gitignored) colored HTML reports
```

**Smart Configuration:** `playwright.config.js` automatically detects `--headed` flag:
- **Headless mode** (default): 4 parallel workers, 2 retries per test, faster execution
- **Headed mode** (--headed flag): 1 worker, 0 retries, serial execution for debugging

---

## Quick Start (new joiners)

### 1️⃣ Setup (run once)

```bash
# Install dependencies
npm install

# Install browser binaries
npx playwright install chromium
```

### 2️⃣ Running Tests

#### **Run All Tests — Headless Mode** (no browser window, fastest)
```bash
npm test
```
This runs all tests in parallel (4 workers) in the background and generates an HTML report.

#### **Run All Tests — Headed Mode** (watch the browser in real-time)
```bash
npm test -- --headed
```
Great for debugging! You'll see the browser window executing all tests.

⚠️ **Important:** Run this from your **system terminal** (not VS Code terminal) to avoid macOS sandbox permission issues with Chromium. Open Terminal.app and navigate to this folder, then run the command.

#### **Run Single Test — Headless Mode** (fastest way to run one test)
```bash
npm test -- Tests/base/loginUsingInvalidCredential.js
```
Runs only the specified test and generates artifacts (logs, screenshots, report).

#### **Run Single Test — Headed Mode** (debug a specific test)
```bash
npm test -- Tests/base/loginUsingInvalidCredential.js --headed
```
Perfect for troubleshooting! Watch the browser while running a single test.

⚠️ **Important:** Run this from your **system terminal** (not VS Code terminal) to avoid macOS sandbox permission issues with Chromium.

#### **Run Tests by Module**
```bash
# Run all login tests (base module)
npm test -- Tests/base/

# Run all admin tests
npm test -- Tests/admin/

# Run all PIM tests
npm test -- Tests/pim/

# Run all in headed mode
npm test -- Tests/base/ --headed
```

#### **Run with Debug Flag** (step through code in VS Code)
```bash
npm test -- --debug
```

### 3️⃣ View Test Reports

After any test run, open the HTML report:
```bash
npm run test:report
```
This shows a colored summary (green = APPROVED, red = NOT APPROVED) with pass rate, counts, and test details.

---

## Command Reference (Quick Copy-Paste)

| Goal | Command |
|------|---------|
| Run all tests, headless | `npm test` |
| Run all tests, headed ⚠️ | `npm test -- --headed` *(run from system terminal)* |
| Run single test, headless | `npm test -- Tests/base/loginUsingInvalidCredential.js` |
| Run single test, headed ⚠️ | `npm test -- Tests/base/loginUsingInvalidCredential.js --headed` *(run from system terminal)* |
| Run module tests | `npm test -- Tests/admin/` |
| Run with debugging | `npm test -- --debug` |
| View HTML report | `npm run test:report` |
| Check last run logs | `cat Logs/Logs_TestRun_*.txt` |

**⚠️ Note:** Headed mode commands must be run from your **system terminal** (Terminal.app), not from VS Code's integrated terminal, to avoid Chromium sandbox permission issues on macOS.

---

## Artifacts (generated per run)

| Artifact | Location | Naming convention |
|---|---|---|
| Screenshots | `ScreenshotAttachment/TestRun_<DateStamp>_<TimeStamp>/` | `<TestName>_PASS_<DateStamp>_<TimeStamp>.png` (passed)<br>`<TestName>_FAIL_<DateStamp>_<TimeStamp>.png` (failed) |
| Logs | `Logs/` | `Logs_TestRun_<DateStamp>_<TimeStamp>.txt` |
| Report | `Reports/` | `TestReport_<DateStamp>_<TimeStamp>.html` |

All three folders are **gitignored** and regenerated on every run.

### ✨ Automatic Cleanup (Smart Retention)

After every test run, the framework **automatically deletes old test runs**, keeping only the **last 5 test runs** across all three artifact folders:
- Logs/ folder
- ScreenshotAttachment/ folder  
- Reports/ folder

This prevents disk space bloat from hundreds of test runs while still maintaining recent history for review. Cleanup happens automatically—no configuration needed!

---

## The 99% Pass-Rate Gate

`Utils/reportGenerator.js` (wired as Playwright's `globalTeardown`) reads the JSON report after every run and produces a colored HTML report with passed/failed counts, passing percentage, and the gate verdict:

- **APPROVED** (green) — pass rate ≥ 99%
- **NOT APPROVED** (red) — pass rate < 99% — no release go-ahead

The same summary is printed to the console.

---

## Understanding Test Files

Each test file is **independent** — it has:
1. **Setup** — logs in with credentials
2. **Test Body** — performs the test actions
3. **Teardown** — captures a PASS/FAIL screenshot automatically

**Example file:** `Tests/base/loginUsingInvalidCredential.js`
```javascript
const { test, expect } = require('../../Base/baseTest');  // Import test + fixture
const config = require('../../config/config');             // Get credentials
const LoginPage = require('../../Pages/loginPage');         // POM class
const BaseSelectors = require('../../Selectors/basePage');  // XPath selectors

test('Verify login with invalid credentials and get error message', async ({ baseTest }) => {
  // 'baseTest' is the fixture that sets up the page + provides helpers
  const loginPage = new LoginPage(baseTest.page);
  await baseTest.login(config.invalidUsername, config.invalidPassword);
  
  // Wait for error message and verify
  await baseTest.waitForElementVisible(BaseSelectors.invalidCredentialAlert);
  expect(await loginPage.isErrorMessageVisible()).toBe(true);
  
  // DONE! Screenshot is captured automatically by teardown.
});
```

---

## Setting Up Credentials (via `.env`)

By default, tests use hardcoded demo credentials:
- **Username:** Admin
- **Password:** admin123

To override for your environment:

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** and set your credentials:
   ```
   BASE_URL=https://your-orangehrm-instance.com/
   VALID_USERNAME=your_username
   VALID_PASSWORD=your_password
   INVALID_USERNAME=invalid_test
   INVALID_PASSWORD=wrong_pass
   PASS_RATE_THRESHOLD=99
   ```

3. **Save & run tests** — they'll use `.env` automatically (gitignored, never committed).

---

## Folder Breakdown for New Joiners

| Folder | Purpose | Who Edits It |
|--------|---------|--------------|
| `Tests/` | **Test cases** — one file per test. Write tests here. | 🔵 **Developers** |
| `Pages/` | **Page Object Model** — methods like `.login()`, `.search()`. Reuse across tests. | 🔵 **Developers** |
| `Selectors/` | **XPath locators** — **NEVER use CSS selectors here**. Update when UI changes. | 🟡 **Test Automation Eng** |
| `Base/` | **Test fixture** — setup, helpers, teardown. Read-only for most. | 🔴 **Framework Owner** |
| `config/` | **Credentials & URLs** — override via `.env`. | 🟡 **Test Automation Eng** |
| `Utils/` | **Logger, screenshots, reports** — internal plumbing. | 🔴 **Framework Owner** |

---

## Page Object Model (POM) — How to Use It

**❌ DON'T do this in tests:**
```javascript
// WRONG! Selectors hardcoded in test
await page.fill("//input[@name='username']", "admin");
```

**✅ DO this:**
```javascript
// RIGHT! Use POM + Selectors
const loginPage = new LoginPage(baseTest.page);
await baseTest.login(config.validUsername, config.validPassword);
```

**Why?** If the UI changes, you update **one file** (`Selectors/basePage.js`) instead of every test.

---

## XPath-Only Locators (mandatory)

Every selector in `Selectors/` **must** be XPath. No CSS selectors allowed.

**✅ Valid XPath examples:**
```javascript
"//input[@placeholder='Username']"           // by placeholder
"//button[@type='submit']"                   // by type
"//span[contains(@class,'oxd-text')]"        // contains class
"//a[text()='Logout']"                       // exact text
"//p[contains(@class,'oxd-alert')]"          // partial match
```

**Why XPath?**
- Works reliably when CSS is complex (OrangeHRM heavily uses dynamic classes)
- More powerful for finding elements by text, attributes, ancestors
- Consistent across the framework

---

## Writing a New Test (Step-by-Step)

### Step 1: Create the Test File
Create `Tests/base/myNewTest.js`:
```javascript
const { test, expect } = require('../../Base/baseTest');
const config = require('../../config/config');
const LoginPage = require('../../Pages/loginPage');

test('My new test title', async ({ baseTest }) => {
  // Your test here
});
```

### Step 2: Use POM Methods
```javascript
const loginPage = new LoginPage(baseTest.page);
await baseTest.login(config.validUsername, config.validPassword);
await baseTest.waitForElementVisible(/* xpath */);
```

### Step 3: Add Assertions
```javascript
expect(await loginPage.isLoggedIn()).toBe(true);
```

### Step 4: Run & Check Report
```bash
npm test -- Tests/base/myNewTest.js --headed
npm run test:report
```

---

## Troubleshooting

### ❌ "Playwright Test did not expect test() to be called here"
**Cause:** Corrupted `node_modules` folder

**Fix:**
```bash
rm -rf node_modules
npm install
npx playwright install chromium
npm test
```

### ❌ Test times out waiting for element
**Cause:** Selector is wrong or element takes too long to load

**Fix:**
```javascript
// Increase timeout (default 15s)
await baseTest.waitForElementVisible(selector, 30000);  // 30 seconds
```

### ❌ Screenshot looks wrong / test passes but UI didn't match
**Cause:** Test ran too fast before page fully loaded

**Fix:** Add a wait before asserting
```javascript
await baseTest.waitForElementVisible(expectedElement);
// Now assert
expect(await loginPage.isErrorMessageVisible()).toBe(true);
```

### ❌ Can't see what's happening (test fails without info)
**Fix:** Run in headed mode
```bash
npm test -- Tests/base/myTest.js --headed
```
Or check the logs:
```bash
cat Logs/Logs_TestRun_*.txt | tail -50
```

### ❌ "Failed to create a ProcessSingleton" or Chromium won't launch in headed mode
**Cause:** VS Code's sandbox environment on macOS has permission restrictions preventing Chromium from creating socket files.

**Fix:** Run headed tests from your **system terminal** instead of VS Code's terminal:
1. Open Terminal.app (not VS Code terminal)
2. Navigate to the framework folder:
   ```bash
   cd /Users/vineetverma/Desktop/Projects/AITester/chapter_02_Prompt_Engineering/OrangePlaywrightFramework
   ```
3. Run headed tests:
   ```bash
   npm test -- --headed
   ```
   Or for a single test:
   ```bash
   npm test -- Tests/base/loginUsingInvalidCredential.js --headed
   ```

**Why?** The system terminal has full file system permissions, while VS Code's integrated terminal uses a sandbox that restricts Chromium's socket directory access on macOS.

---

## Common npm Scripts

Your `package.json` includes these shortcuts:

```bash
npm test                  # Run all tests (headless, parallel)
npm run test:headed       # Run all tests (headed mode)
npm run test:single       # Run a single test or module
npm run test:report       # View the last HTML report
```

---

## The 99% Pass-Rate Gate Explained

After every test run, you see:

```
======================================================================
  ORANGEHRM TEST SUMMARY
======================================================================
  Total tests : 5
  Passed      : 5
  Failed      : 0
  Pass rate   : 100.00%  (threshold: 99%)
  Gate status : APPROVED — release go-ahead granted
```

- **APPROVED** (green) ✅ = Pass rate ≥ 99% → safe to release
- **NOT APPROVED** (red) ❌ = Pass rate < 99% → fix failures before release

(Change threshold in `.env`: `PASS_RATE_THRESHOLD=99`)

---

## Conventions & Best Practices

- **Page Object Model** — tests never touch selectors directly; they call page-object methods.
- **XPath only** — every locator in `Selectors/` is an XPath string (mandatory requirement).
- **One test per file** — files in `Tests/<module>/` map 1:1 to test cases.
- **Single QA environment** — `config/config.js` holds one `baseURL`; no env switching.
- **Secrets in `.env`** — override credentials via `.env` (gitignored); never hardcode real passwords in committed files.
- **Parallelism** — `fullyParallel: true` with 4 workers; tests are independent (each logs in fresh).
- **Descriptive test names** — use `test('Verify login with invalid credentials...')`, not `test('test1')`.
