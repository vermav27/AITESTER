# RICEPOT PROMPT: Local-First Job Application Tracker

## R — ROLE

Act as a senior frontend engineer, product designer, accessibility specialist and careful Git maintainer with expertise in:

* React and TypeScript
* Vite
* IndexedDB and the `idb` library
* `@dnd-kit/core` and `@dnd-kit/sortable`
* Tailwind CSS
* Responsive Kanban interfaces
* Local-first browser applications
* Accessible forms, dialogs and keyboard interactions
* Secure JSON import and export
* Brand-icon integration
* Automated frontend testing
* Static Vercel deployment
* Git-based development workflows
* Technical documentation and development-session handovers

Build production-quality, maintainable code while keeping the application simple and intuitive for a non-technical user.

---

## I — INSTRUCTIONS

Create a simple, local-first Job Application Tracker as a single-page React application.

The application must help one person:

1. Save jobs from any job platform or company careers page.
2. Track jobs through a Kanban workflow.
3. Recognize supported job platforms from their URLs.
4. See a small source-platform logo on each job card.
5. Search, sort, edit and manage applications.
6. Export and restore job data.
7. Learn how to use the tracker through an in-app help guide.
8. Close and reopen the browser without losing changes.
9. Run locally now and remain ready for future Vercel deployment.
10. Continue development safely across multiple coding sessions.

Use three complementary development-continuity mechanisms:

1. **Project files** — The current application implementation and documentation
2. **Git commits** — Reliable, logical snapshots of code changes
3. **`docs/SESSION_LOG.md`** — An append-only record of decisions, progress, verification and remaining work

The UX priorities are:

* Adding a job must be quick.
* Updating its status must be effortless.
* The interface must remain clean and uncluttered.
* Important information must be visible on the cards.
* Saving and storage errors must be clearly communicated.
* Destructive actions must require confirmation.
* Dragging must not be the only way to update status.
* The user must understand where their data is stored.

---

## C — CONTEXT

### Current product scope

This version is local-only.

Do not implement:

* User accounts
* Google authentication
* LinkedIn authentication
* Password authentication
* Multiple-user profiles
* Cloud synchronization
* A backend
* A remote database

The user must be able to open the tracker directly without signing in.

All job records and application settings must be stored in IndexedDB through the `idb` package.

### Persistence expectations

Changes must remain available when the user:

* Reloads the page
* Closes and reopens the browser
* Returns to the same application URL using the same browser profile
* Starts a later application session from the same origin

Data is not expected to follow the user when they:

* Use another browser
* Use another browser profile
* Use another device
* Clear browser or site data
* Switch between localhost and the deployed URL
* Switch between different Vercel preview URLs
* Use private/incognito browsing after that session ends

Explain these limitations in the application and README.

### Future authentication readiness

Do not implement authentication now, but avoid making it unnecessarily difficult to add later.

Use repository-style abstractions such as:

* `JobRepository`
* `SettingsRepository`

Provide IndexedDB implementations for the current version.

Keep UI components dependent on repository interfaces or application-level services rather than directly calling IndexedDB everywhere.

Do not:

* Add fake login screens
* Add unused OAuth packages
* Add placeholder authentication buttons
* Add fake `userId` values
* Pretend that local data is cloud synchronized

Document where future authenticated repositories or synchronization services could be introduced.

### Job data model

Define a typed `Job` model containing:

* `id`: unique string generated with `crypto.randomUUID()`
* `companyName`: required trimmed string
* `role`: required trimmed string
* `jobUrl`: optional HTTP or HTTPS URL
* `resumeName`: optional trimmed string
* `appliedDate`: local date in `YYYY-MM-DD` format or `null`
* `salaryRange`: optional trimmed string
* `notes`: optional trimmed plain-text string
* `status`: one supported status
* `position`: number used for persistent manual ordering
* `createdAt`: ISO timestamp
* `updatedAt`: ISO timestamp

Do not store a manually selected platform name. Derive it from `jobUrl`.

Do not store or render user-entered HTML.

### Kanban statuses

Use exactly these statuses in this order:

1. `wishlist` — Wishlist
2. `applied` — Applied
3. `follow-up` — Follow-up
4. `interview` — Interview
5. `offer` — Offer
6. `rejected` — Rejected

### Applied-date rules

* A new job defaults to Wishlist.
* A Wishlist job initially has no applied date.
* The user may manually provide an applied date for any job.
* When a job is first moved from Wishlist to Applied or a later status, automatically set the applied date to the current local date if it is empty.
* If a job is created directly in Applied or a later status, default the applied date to today unless the user provides another valid date.
* Never overwrite an existing applied date during later status changes.
* Moving a job back to Wishlist must not erase its applied date.
* The user may manually edit or clear the date.
* Do not accept future applied dates.
* Calculate “days since applied” using local calendar-day differences, not elapsed 24-hour periods.
* If no date exists, display “Not applied”.

### Supported job platforms

Initially detect these ten platforms:

| Platform  | Recognized hostnames                                          |
| --------- | ------------------------------------------------------------- |
| LinkedIn  | `linkedin.com`, its valid subdomains and `lnkd.in`            |
| Naukri    | `naukri.com` and its valid subdomains                         |
| Indeed    | `indeed.com` and its valid regional subdomains                |
| Glassdoor | `glassdoor.com`, `glassdoor.co.in` and their valid subdomains |
| Foundit   | `foundit.in` and its valid subdomains                         |
| Wellfound | `wellfound.com` and its valid subdomains                      |
| Instahyre | `instahyre.com` and its valid subdomains                      |
| Cutshort  | `cutshort.io` and its valid subdomains                        |
| Hirist    | `hirist.tech` and its valid subdomains                        |
| IIMJobs   | `iimjobs.com` and its valid subdomains                        |

Treat this as an initial supported-platform set, not an authoritative traffic ranking.

### Platform detection

Create a centralized typed platform registry containing:

* Platform ID
* Display name
* Recognized hostnames
* Icon reference
* Accessible external-link label

Parse URLs using the browser `URL` API.

Normalize the hostname by lowercasing it and handling a leading `www.` safely.

Match only an exact hostname or genuine subdomain using logic equivalent to:

```ts
hostname === domain || hostname.endsWith(`.${domain}`)
```

Examples:

* `jobs.linkedin.com` must match LinkedIn.
* `in.indeed.com` must match Indeed.
* `fake-linkedin.com` must not match LinkedIn.
* `linkedin.com.attacker.example` must not match LinkedIn.

For an unknown platform:

* Show a generic globe or external-link icon.
* Use its hostname as the tooltip and accessible source name.
* Allow the job to be saved.
* Do not request a remote favicon.

### Platform icons

Display a compact source badge when a job URL is available.

Requirements:

* Use an approximately `18 × 18px` logo inside a consistent `24 × 24px` badge.
* Place it near the upper part of the card without competing with the company name.
* Preserve the official proportions.
* Use an approved brand colour or approved monochrome variant.
* Do not stretch, redraw or approximate a trademarked logo.
* Ensure readability in light and dark themes.
* Show a tooltip such as “Open job on LinkedIn”.
* Make the badge keyboard focusable.
* Open the job in a new tab using `noopener noreferrer`.
* Provide an accessible label.

Logo sourcing rules:

1. Prefer an official permitted brand asset.
2. A verified Simple Icons or equivalent icon may be used after reviewing the individual icon’s licensing and brand guidance.
3. Use tree-shaken imports.
4. Keep custom assets inside the repository.
5. Never load logos from runtime favicon services.
6. Never hotlink assets from job websites.
7. Record every included brand asset in `BRAND_ASSETS.md`.
8. Use logos only to identify the job-link source.
9. Do not imply partnership or endorsement.
10. If a verified logo cannot be used, show a generic globe or initial badge instead of inventing one.

### URL validation and normalization

Accept job links from:

* Supported platforms
* Other job boards
* Applicant-tracking systems
* Company careers websites
* Recruiter-shared links

Accept only valid `http://` and `https://` URLs.

Reject protocols including:

* `javascript:`
* `data:`
* `file:`
* `vbscript:`

For duplicate comparison:

* Trim whitespace
* Lowercase the hostname
* Remove fragments
* Remove unnecessary trailing slashes
* Ignore common tracking parameters:

  * `utm_source`
  * `utm_medium`
  * `utm_campaign`
  * `utm_term`
  * `utm_content`
  * `trk`
  * `trackingId`

Preserve unknown query parameters because they may contain the job identifier.

Do not silently rewrite the user’s stored URL beyond safe trimming.

### IndexedDB design

Create a versioned IndexedDB database containing at least:

* A `jobs` object store using `id` as its key
* A `settings` object store for:

  * Theme
  * Sort preference
  * Help-guide seen state
  * Other appropriate UI preferences

Keep initialization and database-upgrade logic isolated.

A failed database write must never be reported as successful.

### First-use experience

Do not automatically insert sample jobs.

When no jobs exist, show:

* A short explanation
* A prominent “Add your first job” button
* A note that data remains in the current browser
* A secondary “How to use tracker?” action

The help guide may automatically open once when:

* No jobs exist
* `hasSeenGuide` is false

After dismissal, do not repeatedly auto-open it.

### “How to use tracker?” guide

Place a small help icon in the application header above the Kanban board.

The button must:

* Remain visible on laptop and tablet layouts
* Have an accessible name
* Show the tooltip “How to use tracker?”
* Open an accessible modal or slide-over

The guide title must be:

> How to use this tracker

Explain:

1. **Add a job** — Enter the company, role and optional job link.
2. **Move it through stages** — Drag a card or use its status menu.
3. **Open the original listing** — Select the platform icon.
4. **Find and organize jobs** — Use search and sorting.
5. **Back up your data** — Export JSON regularly and use Import to restore it.

Include a “Your data stays in this browser” section explaining:

* No login or cloud synchronization exists.
* Browser data can be cleared.
* Different browsers and domains have separate data.
* JSON export is the backup mechanism.

The guide must:

* Trap focus while open
* Work with a keyboard
* Close with Escape when safe
* Have a visible Close button
* Restore focus to the help button
* Work in every theme

### Development continuity

Development must remain understandable across separate coding sessions.

At the beginning of every session:

1. Check whether the directory is a Git repository.
2. Read any applicable `AGENTS.md`, `CONTRIBUTING.md` or equivalent project instructions.
3. Read `README.md`.
4. Read `docs/SESSION_LOG.md`.
5. Run `git status --short`.
6. Review recent history with `git log --oneline -10`.
7. Inspect the actual relevant files before trusting the log.
8. Identify:

   * Completed work
   * Current state
   * Uncommitted changes
   * Known failures
   * Next pending task
9. Append a new session-start entry to the session log.

Treat the source files and test results as the authoritative technical state. Use the session log as development context, not as a replacement for inspecting the code.

---

## E — EXPECTED SUCCESS CRITERIA

### Job management

* Users can create, view, edit and delete jobs.
* Company name and role are required.
* Whitespace-only required values are rejected.
* Invalid or unsafe URLs are rejected.
* Future applied dates are rejected.
* CRUD operations persist immediately after successful completion.
* Reloading restores all saved data.
* Closing and reopening the browser on the same origin restores data.
* Delete requires an accessible confirmation naming the company and role.
* Success notifications appear only after successful persistence.
* IndexedDB errors remain visible until dismissed or resolved.

### Job form

Use one reusable accessible modal or slide-over.

Show primary fields first:

1. Company name
2. Role
3. Status
4. Job URL

Place these under “Additional details”:

* Resume used
* Applied date
* Salary range
* Notes

Requirements:

* Default status is Wishlist.
* Resume name uses editable autocomplete populated from previous entries.
* Show validation beside the affected fields.
* Disable duplicate submissions while saving.
* Ask before discarding unsaved changes.
* Move focus into the dialog.
* Restore focus when it closes.

### Duplicate detection

When adding or editing:

* Compare normalized URLs.
* If another job matches, name the matching company and role.
* Warn without silently blocking the save.
* Let the user continue deliberately.

### Kanban board

* Display all six columns in the defined order.
* Use subtle status accents without relying only on colour.
* Show total counts.
* During search, show `visible / total`.
* Use consistent column widths.
* Scroll the board horizontally on narrower screens.
* Make each column vertically scrollable where appropriate.
* Persist status changes immediately after a successful drop.
* Persist manual ordering.

Provide these sort modes:

* Manual
* Newest
* Oldest

Sorting rules:

* Newest and Oldest use `appliedDate`.
* Jobs without an applied date appear after dated jobs.
* Manual reordering works only in Manual mode.
* Status changes work in all modes.
* In Manual mode, a cross-column move places the card at the top.
* Date-sorted columns automatically re-sort after a move.
* Disable same-column reordering while search is active.
* Continue allowing cross-column status changes while searching.
* A cancelled drag must not mutate data.

Provide a non-drag status selector.

### Job cards

Each card displays:

* Source-platform badge
* Company
* Role
* Resume tag when present
* Days since applied or “Not applied”
* Salary range when present and space permits
* Edit
* Change status
* Delete

The whole card must not be a hyperlink.

Long content may be visually truncated but must not be modified in storage.

### Search

* Search company and role case-insensitively.
* Update results while typing.
* Trim the query.
* Provide a clear-search button.
* Show “No matching jobs” appropriately.
* Never mutate data during search.

### Theme

Provide:

* Light
* Dark
* System

Default to System and persist the choice in IndexedDB.

Maintain accessible contrast, focus indicators and readable logo badges.

### Export and import

Export a JSON backup containing:

* `schemaVersion`
* `exportedAt`
* `jobs`
* `settings`

Include the current local date in the filename.

Import must:

1. Accept a local `.json` file.
2. Parse it safely.
3. Validate the overall structure.
4. Validate every record.
5. Reject unsupported schema versions.
6. Show valid, invalid and conflicting counts before writing.
7. Offer Merge and Replace.
8. Default to Merge.
9. Require explicit confirmation for Replace.
10. Use transactional writes where possible.
11. Preserve the existing database if the import fails.
12. Report imported, skipped and replaced counts.

Merge rules:

* A matching ID or normalized URL is a conflict.
* Preserve the existing job by default.
* Skip and report the incoming conflict.
* Never overwrite silently.

Replace rules:

* Block Replace if any incoming record is invalid.
* Replace only after full validation and explicit confirmation.

Never invent missing fields.

### Accessibility and responsiveness

* All fields have visible labels.
* All controls are keyboard accessible.
* Dialogs use correct semantics.
* Focus states are visible.
* Dragging is optional.
* Touch interactions work on tablets.
* The UI remains usable from approximately 768px upward.
* Prefer horizontal Kanban scrolling over compressed columns.
* Respect `prefers-reduced-motion`.

### Vercel readiness

Prepare for future Vercel deployment without deploying now.

Requirements:

* `npm run build` outputs to `dist`.
* Use Vite-compatible asset paths.
* Do not hardcode localhost URLs.
* Do not require secrets or environment variables.
* Include valid SPA fallback configuration when needed.
* Refreshing the deployed application must not cause an avoidable 404.
* Document Git-import and Vercel CLI deployment.
* State that Vercel hosts only the static frontend.
* State that job data remains inside each browser and origin.
* Do not add Vercel Functions, server storage or analytics.
* Do not deploy or create external resources without authorization.

### Project-file continuity

The repository must include:

* Application source code
* Tests
* Configuration
* `README.md`
* `BRAND_ASSETS.md`
* `docs/SESSION_LOG.md`
* Appropriate `.gitignore`
* Vercel configuration when needed

Do not depend on untracked local files for application behaviour.

Do not commit:

* `node_modules`
* Build output unless specifically required
* Coverage output
* Temporary files
* Secrets
* Tokens
* OAuth credentials
* Personal job data
* Exported user backup files
* Private environment files

### Session log

Create and continuously maintain:

```text
docs/SESSION_LOG.md
```

The log must be append-only. Never erase or rewrite previous valid entries to make history appear cleaner.

Use entries similar to:

```md
## 2026-09-17T12:30:00Z — Session 01

### Goals
- ...

### Requirements and decisions
- ...

### Work completed
- ...

### Files changed
- Added: ...
- Modified: ...
- Deleted: ...

### Dependencies
- Added: ...
- Removed: ...

### Database or schema changes
- ...

### Verification
- `npm run lint` — passed/failed
- `npm test` — passed/failed
- `npm run build` — passed/failed

### Problems and resolutions
- ...

### Known limitations
- ...

### Next recommended task
- ...

### Session status
- Complete / Partial / Blocked
```

Log rules:

* Use ISO 8601 UTC timestamps.
* Add an entry at the start and update it throughout the session.
* Record meaningful decisions when they are made.
* Record actual results, not intended results.
* Summarize long command output and include the exit status.
* Record failures as well as successes.
* Append corrections instead of silently rewriting history.
* Never include secrets, credentials or environment-variable values.
* Never include private user job records or imported backup content.
* Keep entries concise enough to be useful to the next developer.

### Git history

Use Git as a deliberate project history.

If the directory is not already a Git repository:

* Initialize Git only for this project directory.
* Create an appropriate `.gitignore`.
* Do not modify global Git configuration.

If it is already a repository:

* Preserve its existing history.
* Preserve unrelated user changes.
* Do not include unrelated files in project commits.
* Inspect the working tree before staging.

Create logical commits after meaningful verified phases. Suggested commit structure:

1. `chore: scaffold local job tracker`
2. `feat: add indexeddb persistence`
3. `feat: build accessible kanban workflow`
4. `feat: add job platform source badges`
5. `feat: add help backup and restore workflows`
6. `test: cover critical tracker behavior`
7. `docs: finalize deployment and session handoff`

These are examples; use accurate messages matching the actual changes.

Git safety requirements:

* Stage only intended project files.
* Review the staged diff before committing.
* Do not use destructive reset or checkout commands.
* Do not rewrite existing history.
* Do not amend, rebase or force-push without explicit instruction.
* Never push to a remote.
* Never create a pull request.
* Never invent a Git author identity.
* If Git identity, signing or hooks prevent a commit, record the blocker and report it instead of bypassing safeguards.
* Do not claim a commit exists unless it was created successfully.
* Do not claim the tree is clean without checking it.

At the end of the session:

1. Update `docs/SESSION_LOG.md`.
2. Run the required verification.
3. Review `git diff`.
4. Review staged changes.
5. Create the appropriate logical commit if permitted.
6. Run `git status --short`.
7. Run `git log --oneline -10`.
8. Report uncommitted files and blockers accurately.

### Verification

Before completion:

* Install dependencies successfully.
* Run linting.
* Run automated tests.
* Run the production build.
* Preview the production build locally.
* Check for runtime console errors during core workflows.

Add tests for:

* Required-field validation
* Safe URL validation
* URL normalization
* All ten platform mappings
* Valid subdomain matching
* Lookalike-domain rejection
* Date calculation
* Automatic applied-date behaviour
* Search
* Sort behaviour
* Import validation
* Merge conflicts
* IndexedDB persistence where practical

Manually verify:

* Create
* Edit
* Delete
* Reload persistence
* Browser close-and-reopen persistence where practical
* Dragging
* Status selection without dragging
* Manual reordering
* Sorting
* Searching
* Supported platform badges
* Unknown-platform fallback
* Help guide
* Theme selection
* Export
* Merge import
* Replace import
* Production preview

Do not claim a check passed unless it was performed.

---

## P — PARAMETERS

### Required technology

* React 18 or compatible newer stable version
* TypeScript
* Vite
* Functional components and hooks
* Tailwind CSS
* `idb`
* `@dnd-kit/core`
* `@dnd-kit/sortable`
* Lightweight Vite-compatible testing

For icons:

* Use a lightweight UI icon set for generic controls.
* Use verified local SVG assets or tree-shaken brand-icon imports.
* Do not load an entire icon library unnecessarily.
* Do not use runtime favicon services.

### Architecture constraints

* No backend
* No authentication
* No user profiles
* No cloud database
* No cloud synchronization
* No analytics
* No advertisements
* No scraping
* No job-platform APIs
* No background runtime metadata lookup
* No background runtime logo lookup
* No Redux unless a concrete need is demonstrated
* No unsafe HTML rendering
* No mock persistence
* No destructive migrations
* No non-functional placeholders

User-initiated navigation to a saved job URL is allowed.

Use clearly named modules for:

* Types
* Constants
* Repository interfaces
* IndexedDB repositories
* Database migrations
* Validation
* Dates
* URL normalization
* Platform detection
* Platform icons
* Import/export
* Board
* Columns
* Cards
* Job form
* Help guide
* Confirmation
* Notifications

### UX constraints

* Keep the product on one primary page.
* Avoid dashboards and unrelated features.
* Use plain labels.
* Prefer discoverable actions.
* Do not overcrowd cards.
* Use a restrained professional style.
* Avoid excessive animation.
* Do not use colour as the only signal.
* Keep the help action easy to locate without making it visually dominant.

### Development constraints

* Inspect before editing.
* Preserve existing work.
* Use the project’s existing package manager if one is already established.
* Do not replace working configuration without a demonstrated reason.
* Keep changes inside the project scope.
* Maintain the session log while working, not only retrospectively.
* Use logical Git commits rather than one unexplained final commit.
* Never commit secrets or private user data.

### Local environment

* Use a fixed Vite port, preferably `5173`.
* Enable `strictPort`.
* Document IndexedDB’s origin dependency.
* Provide development, test, build and preview commands.
* Do not require application-data API calls after dependency installation.
* A PWA or service worker is not required.

---

## O — OUTPUT FORMAT

Create the complete runnable project in the current working directory.

Deliver:

1. Complete application source
2. Clean project structure
3. TypeScript data models
4. Repository interfaces
5. IndexedDB repository implementation
6. Database schema and migrations
7. Responsive Kanban board
8. Accessible forms and dialogs
9. Central platform registry
10. Verified local platform icons or safe fallbacks
11. Import/export implementation
12. Help guide
13. Automated tests
14. Vercel-ready configuration
15. `.gitignore`
16. `README.md`
17. `BRAND_ASSETS.md`
18. `docs/SESSION_LOG.md`
19. Logical Git commits
20. Final implementation summary
21. Assumptions and limitations
22. Exact verification commands and actual results
23. Final `git status --short`
24. Recent `git log --oneline` summary
25. Any blockers or uncommitted files

The README must explain:

* What the tracker does
* Prerequisites
* Installation
* Development
* Testing
* Production build
* Production preview
* IndexedDB storage
* Same-browser persistence
* Origin limitations
* Backup and restore
* Vercel Git deployment
* Vercel CLI deployment
* Future authentication extension points

Do not provide only pseudocode, disconnected snippets or a visual mock-up.

---

## T — TASK

Implement the complete local-first Job Application Tracker.

Follow this sequence:

1. Inspect the working directory.
2. Read project instructions if present.
3. Inspect Git status and recent history.
4. Read the README and existing session log.
5. Preserve unrelated changes.
6. Start or append the current session-log entry.
7. Initialize Git only if necessary and safe.
8. Scaffold or configure the Vite React TypeScript application.
9. Install only necessary dependencies.
10. Define the data model and repository interfaces.
11. Implement IndexedDB repositories and migrations.
12. Implement validation, dates and URL utilities.
13. Implement platform detection.
14. Verify and integrate permitted platform icons.
15. Document brand assets.
16. Build the responsive Kanban board.
17. Implement drag-and-drop and non-drag status controls.
18. Build the accessible create/edit experience.
19. Implement search and sorting.
20. Implement source badges and external links.
21. Implement confirmation and notifications.
22. Implement themes.
23. Implement the help experience.
24. Implement export and import.
25. Add Vercel-ready configuration and documentation.
26. Add focused automated tests.
27. Update the session log throughout development.
28. Run linting, tests and the production build.
29. Preview and manually verify the application.
30. Fix discovered errors.
31. Review diffs and staged changes.
32. Create logical Git commits when permitted.
33. Update the final session-log status.
34. Report verified results, recent commits, working-tree status and limitations.

Do not deploy, push, create a pull request or create external resources without explicit authorization.

---

# ANTI-HALLUCINATION RULES

1. Do not invent package APIs, browser APIs, icon names or command results.
2. Inspect the project before assuming its structure.
3. Verify third-party APIs against installed versions or official documentation.
4. Do not claim installation succeeded unless it did.
5. Do not claim linting, tests or builds passed unless they were run successfully.
6. Do not fabricate manual-test results, screenshots or coverage.
7. Do not simulate IndexedDB persistence with arrays or `localStorage`.
8. Do not silently fall back to memory when IndexedDB fails.
9. Do not report failed writes as successful.
10. Do not claim browser storage is permanent.
11. Do not claim data synchronizes across browsers, origins or devices.
12. Do not add or imply authentication in the current version.
13. Do not create fake users or fake OAuth flows.
14. Do not claim the supported platforms are an authoritative ranking.
15. Do not invent, redraw or approximate brand logos.
16. Verify every included brand asset.
17. Do not imply affiliation with job platforms.
18. Do not fetch favicons at runtime.
19. Do not use unsafe hostname substring matching.
20. Test malicious lookalike hostnames.
21. Do not invent missing import values.
22. Do not silently discard invalid or conflicting imports.
23. Do not introduce analytics, telemetry, scraping or background data requests.
24. Do not claim Vercel stores the user’s jobs.
25. Do not claim different Vercel URLs share IndexedDB.
26. Do not fabricate session-log history.
27. Do not rewrite old log entries to hide mistakes.
28. Do not claim a Git commit exists unless it succeeded.
29. Do not invent Git identity or bypass repository protections.
30. Do not commit secrets, credentials, tokens or personal job records.
31. Do not stage or commit unrelated user changes.
32. Do not use destructive Git commands.
33. Do not push or deploy without explicit authorization.
34. Do not treat the session log as proof that the current source code works.
35. Inspect and verify the actual project state at the beginning of every new session.
36. Prefer a clearly disclosed limitation over an unverified claim.
