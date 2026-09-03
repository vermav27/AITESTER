# Test Plan - KAN-1: Login Page of app.vwo.com

> Status: Draft for human review. This test plan is not final until reviewed and approved by the tester/product owner.

## Document Information

| Field | Details |
|---|---|
| Project / Application Name | VWO / Wingify |
| Module / Feature | Login page for app.vwo.com / app.wingify.com transition |
| Jira Ticket | KAN-1 |
| Jira Type | Story |
| Priority | High |
| Jira Status | In Progress |
| Version / Release | Not specified in ticket |
| Prepared By | QA Draft |
| Reviewed By | Pending |
| Approved By | Pending |
| Date Created | 03-Sep-2026 |
| Last Updated | 03-Sep-2026 |
| Document Status | Draft / In Review |

## Source Requirement Summary

KAN-1 covers the login page for app.vwo.com. Existing users should be able to access the VWO/Wingify application through email and password login or supported alternative authentication methods. The page uses a dark split-screen layout with the login form on the left and a VWO x AB Tasty / Wingify information panel on the right.

The ticket references one design attachment: `Design.png`. The design was reviewed for this draft and shows email, password, password visibility toggle, forgot password, remember me, sign in, Google sign-in, SSO sign-in, passkey sign-in, free trial, privacy policy, terms, and learn more controls.

## 1. Scope & Objectives

### Business Objective

Provide existing VWO/Wingify users with a secure, clear, and usable authentication entry point while communicating that app.vwo.com has transitioned to app.wingify.com and that user plans, features, and data remain unchanged.

### Testing Objective

Validate that the login page:

- Renders according to the ticket and design attachment.
- Supports email and password authentication.
- Supports Google, SSO, and passkey authentication entry points.
- Provides expected navigation for password recovery, free trial signup, privacy policy, terms, and transition information.
- Handles invalid input and failed authentication safely.
- Meets baseline usability, accessibility, compatibility, and security expectations for a login page.

### In Scope

| Area | Description |
|---|---|
| UI Layout | Verify dark theme, split layout, branding, form placement, visual hierarchy, and responsive behavior. |
| Email / Password Login | Validate successful and unsuccessful login attempts. |
| Password Field Behavior | Validate masked input, show/hide toggle, keyboard focus, and no unintended persistence. |
| Remember Me | Validate checkbox behavior and expected session persistence once requirement is clarified. |
| Forgot Password | Validate navigation and recoverability path. |
| Alternative Authentication | Validate Google, SSO, and passkey sign-in entry points and failures/cancellations. |
| New User Path | Validate "Start a FREE TRIAL" navigation. |
| Legal / Consent Links | Validate Privacy Policy and Terms navigation. |
| Transition Panel | Validate VWO x AB Tasty branding, transition copy, and Learn More navigation. |
| Negative / Edge Cases | Validate blank, invalid, malformed, blocked, and failed authentication states. |
| Compatibility | Validate supported desktop/mobile browsers once matrix is confirmed. |
| Accessibility | Validate keyboard navigation, visible focus, labels, contrast, and screen-reader semantics. |
| Security Checks | Validate login-specific security expectations such as secure transport, safe errors, session behavior, and no sensitive data exposure. |

### Out of Scope

| Item | Reason / Notes |
|---|---|
| Full account creation flow after selecting free trial | Ticket only covers the login page entry point. |
| Full password reset workflow beyond link handoff | Ticket only identifies the forgot password entry point. |
| Backend identity provider implementation | Test only the login page integration behavior unless backend auth changes are included elsewhere. |
| Plan/data migration validation after app.wingify.com transition | Ticket only states plans, features, and data remain unchanged; no migration requirements are provided. |

## 2. Gaps & Questions for the Author

### Requirement Checklist

| Checklist Item | Status | Notes / Question |
|---|---|---|
| Clear user story / goal | Ambiguous | Goal is described, but not in a formal user-story format. Confirm target user types. |
| Acceptance criteria are testable | Missing | No explicit acceptance criteria are listed. Please confirm pass/fail criteria. |
| Happy path fully described | Present | Valid email/password login and alternate auth entry points are described. |
| Negative / error paths described | Missing | Define expected behavior for invalid credentials, locked users, unverified users, provider failures, and network errors. |
| Boundary and empty states | Missing | Define behavior for blank email, malformed email, max length, whitespace, blank password, and very long password. |
| State transitions / workflow steps | Ambiguous | Clarify redirects after login, forgot password, SSO, passkey, free trial, legal links, and learn more. |
| Required test data specified | Missing | Need valid, invalid, locked, SSO-enabled, passkey-enabled, Google-enabled, and non-existing users. |
| Environment / config / feature flags named | Ambiguous | URLs are mentioned, but QA/staging environment and any transition flags are not specified. |
| External dependencies listed | Ambiguous | Google, SSO, passkey, privacy/terms, and learn-more destinations are implied but not defined. |
| Preconditions / setup stated | Missing | Required accounts, browser state, cookies, redirects, and tenant setup are not specified. |
| Performance / load expectations | Missing | Define login page load time and authentication response expectations. |
| Security / authorization expectations | Ambiguous | "Securely access" is stated, but no concrete security acceptance criteria are listed. |
| Accessibility expectations | Missing | No WCAG target, keyboard behavior, labels, or contrast expectations are specified. |
| Internationalization / localization | Missing | No supported locales, copy source, timezone, or regional behavior is specified. |
| Audit / logging / observability | Missing | No auth event logging, monitoring, or alerting expectations are specified. |
| Impact on existing features | Ambiguous | Regression surface for existing login, sessions, cookies, and redirects is not described. |
| Backward compatibility / migration | Ambiguous | Transition copy says data remains unchanged, but validation scope is not stated. |
| Mobile / responsive / browser matrix | Missing | Design appears desktop-oriented; supported devices and browsers are not listed. |
| Rollback / feature-flag behavior | Missing | No rollback or feature flag behavior is defined for app.vwo.com to app.wingify.com transition. |
| Ambiguous wording | Ambiguous | Terms like "secure", "clear", "user-friendly", and "plans/features/data remain unchanged" need measurable criteria. |
| Terms defined consistently | Ambiguous | Ticket uses VWO, Wingify, app.vwo.com, app.wingify.com, and AB Tasty; confirm naming rules. |
| Mockups / designs linked and match text | Present | `Design.png` is attached and matches the major controls described in the ticket. |

### Open Questions

1. What is the expected post-login destination for app.vwo.com and app.wingify.com?
2. Should app.vwo.com redirect to app.wingify.com before login, after login, or remain as an alias?
3. What exact error messages should be shown for invalid email, invalid password, disabled account, locked account, unverified email, rate limiting, and network failure?
4. What does "Remember me" do: remember email only, extend session duration, keep user signed in, or something else?
5. Which identity providers and SSO configurations are supported in QA for this story?
6. What browsers, devices, and screen sizes are officially supported?
7. What WCAG level and accessibility checks are required?
8. Are Privacy Policy, Terms, Learn More, Forgot Password, Google, SSO, Passkey, and Free Trial expected to open in the same tab or a new tab?
9. Are there analytics, audit logs, or security events that must fire for login attempts and link clicks?
10. Is the VWO x AB Tasty transition panel copy final and approved by brand/legal?

## 3. Test Scenarios

| ID | Priority | Traceability | Scenario | Expected Validation |
|---|---|---|---|---|
| KAN-1-TS-001 | P0 | Ticket description, design | Load the login page on the target URL. | Page loads successfully, uses the dark split layout, and shows the complete login form and branding panel. |
| KAN-1-TS-002 | P0 | Ticket description | Sign in with a valid registered email and password. | User is authenticated and routed to the expected post-login destination. |
| KAN-1-TS-003 | P0 | Gap: negative paths | Attempt sign-in with invalid credentials. | User is not authenticated, receives a safe error, and no sensitive detail is exposed. |
| KAN-1-TS-004 | P0 | Gap: empty states | Attempt sign-in with blank email and/or blank password. | Required-field validation appears and sign-in is blocked. |
| KAN-1-TS-005 | P0 | Ticket description, design | Validate password show/hide icon behavior. | Password toggles between masked and visible states without changing the entered value. |
| KAN-1-TS-006 | P0 | Ticket description | Select "Forgot Password?". | User is routed to the correct password recovery flow. |
| KAN-1-TS-007 | P0 | Ticket description | Select "Sign in with Google". | Google authentication flow starts correctly and returns to the application after success/cancel/failure. |
| KAN-1-TS-008 | P0 | Ticket description | Select "Sign in using SSO". | SSO flow starts correctly and handles valid, invalid, and cancelled provider responses. |
| KAN-1-TS-009 | P0 | Ticket description | Select "Sign in with Passkey". | Passkey authentication prompt starts where supported and shows a graceful fallback where unsupported. |
| KAN-1-TS-010 | P0 | Gap: security | Verify login page and auth requests use secure transport. | Page and submitted authentication data use HTTPS with no sensitive values exposed in URLs, logs, or client storage. |
| KAN-1-TS-011 | P1 | Ticket description, question | Validate "Remember me" behavior. | Checkbox can be toggled and persistence behavior matches clarified requirement. |
| KAN-1-TS-012 | P1 | Ticket description, design | Select "Start a FREE TRIAL". | User is routed to the expected signup/trial flow. |
| KAN-1-TS-013 | P1 | Ticket description | Select Privacy Policy and Terms links. | Links route to the correct legal pages and are accessible from the login form. |
| KAN-1-TS-014 | P1 | Ticket description, design | Validate transition panel content. | Panel displays VWO x AB Tasty branding, welcome copy, transition message, and Learn More CTA. |
| KAN-1-TS-015 | P1 | Ticket description | Select "Learn More". | User is routed to the expected transition information page. |
| KAN-1-TS-016 | P1 | Gap: validation | Enter malformed email values and boundary-length inputs. | Client/server validation handles malformed, whitespace, max-length, and unusual email formats consistently. |
| KAN-1-TS-017 | P1 | Gap: auth failures | Simulate provider/network failure during Google, SSO, or passkey login. | User receives recoverable feedback and can retry or choose another login method. |
| KAN-1-TS-018 | P1 | Gap: compatibility | Test supported desktop browsers. | Layout, controls, links, and auth entry points work in supported browser matrix. |
| KAN-1-TS-019 | P1 | Gap: responsive | Test tablet and mobile widths. | Page remains usable, controls are visible, text does not overlap, and key actions remain reachable. |
| KAN-1-TS-020 | P1 | Gap: accessibility | Validate keyboard-only navigation and focus order. | All fields, buttons, links, checkbox, and password toggle are reachable and visibly focused. |
| KAN-1-TS-021 | P1 | Gap: accessibility | Validate labels and screen-reader names. | Email, password, remember me, sign-in buttons, legal links, and password toggle have meaningful accessible names. |
| KAN-1-TS-022 | P1 | Gap: accessibility | Validate color contrast in dark theme. | Text, controls, borders, focus indicators, and disabled/error states meet agreed contrast target. |
| KAN-1-TS-023 | P2 | Gap: observability | Validate analytics/audit events if required. | Login attempts, success/failure, and CTA clicks are logged according to clarified tracking requirements. |
| KAN-1-TS-024 | P2 | Gap: localization | Validate copy behavior for supported locales if applicable. | Localized copy fits without truncation or overlap and routes remain correct. |
| KAN-1-TS-025 | P2 | Regression surface | Validate existing session behavior. | Already authenticated users, expired sessions, logout, and direct login URL access behave as expected. |

## 4. Test Data & Environment

### Environment

| Environment | URL / Endpoint | Purpose | Status |
|---|---|---|---|
| QA / Staging | To be confirmed | Functional, integration, and regression testing | Needed |
| Production-like / Pre-Production | To be confirmed | Final validation before release | Needed |
| Production | app.vwo.com / app.wingify.com | Optional smoke checks after release approval | Restricted / pending approval |

### Test Data

| Data Type | Needed For | Status |
|---|---|---|
| Valid registered user | Email/password successful login | Needed |
| Invalid/non-existing user | Negative login validation | Needed |
| User with wrong password attempts | Invalid credential handling | Needed |
| Locked/disabled account | Auth failure handling | Needed |
| Unverified account | Auth failure handling | Needed |
| Google-enabled account | Google authentication | Needed |
| SSO-enabled tenant/user | SSO authentication | Needed |
| Passkey-enabled account/device | Passkey authentication | Needed |
| Browser/device matrix | Compatibility and responsive testing | Needed |

## 5. Test Strategy

### Testing Types

| Test Type | Priority | Notes |
|---|---|---|
| Smoke Testing | P0 | Verify page load, visible form, sign-in action, and critical navigation. |
| Functional Testing | P0 | Validate login methods, field behavior, links, and transition panel. |
| Negative Testing | P0 | Validate invalid credentials, blank fields, malformed inputs, and provider failures. |
| Integration Testing | P0/P1 | Validate identity provider handoffs and return behavior. |
| Security Testing | P0/P1 | Validate secure transport, safe errors, session behavior, and no sensitive exposure. |
| Accessibility Testing | P1 | Validate keyboard access, labels, contrast, and focus behavior. |
| Compatibility Testing | P1 | Validate agreed browser and device support matrix. |
| Regression Testing | P1 | Validate existing auth/session behavior remains intact. |
| Exploratory Testing | P2 | Explore browser state, cookies, autofill, back-button behavior, and unusual auth interruptions. |

### Defect Reporting Procedure

1. Confirm the issue is reproducible on the agreed test environment.
2. Capture browser, OS, viewport, build/version, account type, and authentication method.
3. Attach screenshots or screen recordings for UI issues.
4. Capture console/network evidence for login or redirect failures.
5. Link each defect to `KAN-1` and the relevant scenario ID.
6. Retest fixes and run targeted regression around login/session behavior.

## 6. Risks & Assumptions

### Risks

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| No explicit acceptance criteria | High | High | Use this plan as draft and obtain author confirmation before sign-off. |
| Identity provider test setup unavailable | High | Medium | Confirm Google, SSO, and passkey test accounts early. |
| Remember-me behavior undefined | Medium | High | Clarify expected persistence before execution. |
| Browser/device matrix missing | Medium | Medium | Agree support matrix before compatibility testing. |
| Transition behavior between app.vwo.com and app.wingify.com unclear | High | Medium | Confirm redirect and post-login behavior. |
| Security requirements are vague | High | Medium | Confirm auth/session/security acceptance criteria with engineering/security. |
| Design/copy may change | Medium | Medium | Re-check latest design attachment before execution. |

### Assumptions

- `Design.png` is the current approved design for `KAN-1`.
- The login page is for existing users; full signup and password reset flows are limited to link handoff unless separate requirements are provided.
- Alternative authentication methods are entry points on this page; provider-side internals are out of scope unless changed by this story.
- Production validation, if any, will be smoke-only and approved separately.
- Any credentials, tokens, or restricted access details will be managed outside this test plan.

## 7. Entry / Exit Criteria

### Entry Criteria

- Requirements and open questions are reviewed by the product owner or ticket author.
- QA/staging URL is available.
- Build containing `KAN-1` is deployed.
- Test accounts are available for email/password, Google, SSO, and passkey flows.
- Expected redirects and link destinations are confirmed.
- Supported browser/device matrix is confirmed.

### Exit Criteria

- P0 scenarios are executed and passed or have approved risk acceptance.
- P1 scenarios are executed or formally deferred.
- No open blocker/critical defects remain for login, authentication, or account access.
- High-severity defects are fixed, deferred with approval, or documented as known risk.
- Regression coverage for existing login/session behavior is completed.
- Test evidence and defect links are attached to the execution report.

## 8. Test Schedule & Deliverables

| Deliverable | Description | Owner | Status |
|---|---|---|---|
| Test Plan | Draft plan for `KAN-1` | QA | Draft |
| Test Scenarios | Risk-prioritized scenarios in this document | QA | Draft |
| Test Cases | Detailed executable cases after review approval | QA | Pending |
| Test Data | Accounts and provider setup | QA / Dev / Product | Pending |
| Defect Reports | Issues raised during execution | QA | Pending |
| Test Summary | Execution and risk summary after testing | QA | Pending |

Planned duration is to be confirmed after scope, environments, and identity-provider readiness are approved.

## 9. Human Review Gate

This plan requires human review before it is treated as approved.

### Assumptions Made

- The attached design is current and approved.
- The listed controls are all expected to be functional on the login page.
- Alternative authentication provider internals are not in scope beyond login-page handoff and return behavior.
- Security, accessibility, analytics, and compatibility expectations should be clarified before execution sign-off.

### Cannot Confirm Yet

- Formal acceptance criteria.
- QA/staging URL and build version.
- Expected post-login destination and redirect behavior.
- Exact validation and error messages.
- Identity provider test configuration.
- Remember-me persistence behavior.
- Supported browser/device matrix.
- Required analytics, audit logs, or monitoring.

### Approval Request

Please review the open questions and assumptions above. Approve or edit this draft before detailed test cases or automation are created.
