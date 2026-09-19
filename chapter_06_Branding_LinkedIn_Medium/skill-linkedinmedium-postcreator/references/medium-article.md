# Medium article (piece 4)

The article is the spine at full length. It uses the same hook, the same numbers and the same steps as the LinkedIn post, but each step becomes a mini-lesson with a table, code or a checklist that a reader can act on. Target 1,000–1,800 words, aiming for about 1,300.

## Header block

**Title**: at most 12 words, containing a number or a named tool. When Vineet's title is a question, turn it into a statement.

| Formula | Example |
| --- | --- |
| "[From] to [To] in [Time]: The [N]-Step Formula That Works" | "Manual Tester to Automation in 90 Days: The 7-Step Formula That Works" |
| "How I [result with a number] With [Tool]" | "How I Cut Salesforce Regression From 5 Days to 3 Hours With Playwright" |
| "[N] [Things] I Check Before [Decision]" | "3 Numbers I Check Before Saying Go on a Release" |
| "Why [Common Practice] Is [Costing You Something]" | "Why Rerunning Flaky Tests Is Costing You Real Bugs" |

**Subtitle**: the stake plus the promise, in 1–2 sentences.

> "2027 is the last year "manual-only" works as a career plan. Here are the exact 90 days I'd give anyone starting tomorrow."

**Tags**: exactly 5, chosen from Software Testing, Test Automation, Playwright, TypeScript, QA, Quality Assurance, Salesforce, CI/CD, Career Change, Artificial Intelligence, DevOps.

## Section blueprint

| Section | Heading | Words | Job |
| --- | --- | --- | --- |
| Opening | none | 120–160 | Repeat the hook exactly. Then "That line is meant to sting" (or similar), plus why the underlying skill still matters. End with the good news: "the gap is smaller than it looks". |
| Setup | `### I [started manual too / was the only QA on...]` | 100–160 | 2–3 fact-sheet proof points, anonymised. End on a one-line thesis ("The switch is not a talent. It is a schedule."). |
| Tension | `### Why most [audience] stall` | 120–180 | 3 failure modes, one short paragraph each. Then one line saying the formula closes those gaps. |
| Turn | `### The [N]-step formula` | 700–1,000 | Bold numbered steps (`**1. [Verb phrase].**`), each 2–5 sentences. Across all steps, include **one table**, **one code block** and **one bullet list**. |
| Lesson | `### What I'd do if I started tomorrow` | 100–150 | 5–6 bullets of concrete actions, including at least one real command. |
| Close | none | 60–90 | A pull quote from the line bank (`> ...`), then the offer paragraph ending in "so no judgment here", then his italic bio. |

Headings use `###` inside the reply, because the pack itself uses `##` for piece labels. They paste into Medium as headings.

## Writing rules

- Use paragraphs of 2–4 sentences. Medium readers accept more depth than LinkedIn readers, but not walls of text.
- The Tension section describes behaviour, not people. "They hop between tools" is fine; "lazy testers" is not.
- Every step keeps his original advice and numbers. Where you add depth (why TypeScript, what the exercises look like), it has to be accurate, standard practice.
- Use at most three "isn't X, it's Y" style lines in the whole article.
- Keep the same banned words, the same fact-sheet rule, and the same anonymised client names as everywhere else.

## Code rules

Readers will copy the snippets, and QA readers will notice bad practice immediately, so the code has to be clean.

- Default to Playwright Test with TypeScript, unless the topic is about another tool.
- Use role, label and text locators first (`getByRole`, `getByLabel`, `getByText`), with no XPath.
- Use web-first assertions such as `await expect(locator).toBeVisible()`, and never `waitForTimeout` or hard sleeps.
- Read credentials from `process.env`; never hard-code them.
- Comment non-obvious config, for example `// baseURL is set in playwright.config.ts`.
- Keep each snippet to about 15 lines or fewer.
- When the audience is manual testers, show a manual test case next to its Playwright version. That mapping is what makes code feel familiar to them.
- Use only real commands: `npm init playwright@latest`, `npx playwright test`, `npx playwright show-report`, `npx playwright codegen`.

This is the approved mapping example:

````
```
TC-014: Login with valid credentials
1. Open the login page
2. Enter a valid email and password
3. Click "Sign in"
Expected: the dashboard shows "Welcome back"
```

```ts
import { test, expect } from '@playwright/test';

// baseURL is set in playwright.config.ts
test('TC-014: login with valid credentials', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
});
```
````

## Table rules

Use one table per article. Usually it's the roadmap (Month | Focus | Topics) or a before/after comparison. Keep it to 3–6 rows, with specific topics in the cells rather than categories.

This is the approved roadmap:

| Month | Focus | Topics |
|---|---|---|
| 1 | The language | Variables and types, functions, arrays and objects, loops, async/await and promises, modules, TypeScript basics |
| 2 | Playwright core | Locators (getByRole, getByLabel, getByText), web-first assertions, fixtures and hooks, API testing, debugging with the trace viewer |
| 3 | The framework | Page Object Model, environment config, test data, parallel runs, HTML reports, running the suite in CI (GitHub Actions or Jenkins) |

## Safety line

When the article tells readers to publish work on GitHub, include this line (or a close variant):

> "One rule outranks everything here: never push your employer's code, URLs or test data. Rebuild the idea on a public app instead."

## Close and bio

Put the pull quote on its own line:

> Automation doesn't replace judgment. It buys you time to use it.

The offer paragraph follows the pattern "If you start this week, tell me on LinkedIn which step you're on. I started manual too, so no judgment here."

Use this bio, in italics, as the last line:

*I'm Vineet Verma, a QA lead with 10+ years of owning release quality for Salesforce, Dynamics 365 and healthcare platforms. I write about what it takes to decide what ships. Find me on LinkedIn at linkedin.com/in/vverma1992 and GitHub at github.com/vermav27.*

## Formatting in the reply

````
## Medium article

**Title:** ...

**Subtitle:** ...

**Tags:** ...

---

[opening, no heading]

### [Setup heading]
...
### What I'd do if I started tomorrow
...
> [pull quote]

[offer paragraph]

*[bio]*

---
````
