# NextGen Job Tracker

A simple local-first Job Application Tracker built as a single-page React application. It helps one person review application metrics, save job leads, move applications through a Kanban workflow, recognize common job-platform URLs, export backups, and restore data later.

## Application Views

- **Dashboard** opens by default and shows live totals for every job status, an accessible status-distribution chart, and company lists for Offer and Rejected outcomes.
- **Job Tracker Board** contains the complete Kanban workflow, search, sorting, drag-and-drop and non-drag status controls.

Dashboard values are calculated from the same in-memory job collection loaded from IndexedDB. Switching views does not change saved data, and board search remains available when returning to the board during the same page session.

## In-App User Guide

Open **How to use tracker?** and choose **View User Guide** to read the bundled five-page guide without leaving the application. The PDF.js viewer provides Previous, Next, 75%-175% zoom, reset zoom, retry, and Back to Help controls. It also extracts each page's text for an assistive description.

The viewer intentionally provides no download, print, open-in-new-tab, native browser toolbar, or raw-file-link controls. Because this is a static frontend and the PDF must be delivered to the browser for rendering, those interface restrictions discourage casual downloading but cannot make the document unrecoverable through browser developer tools, caches, or screenshots.

## Prerequisites

- Node.js 20.16 or newer
- npm 10.x or newer
- A modern browser with IndexedDB enabled

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Vite runs on the fixed port `5173` with `strictPort` enabled. Open:

```text
http://127.0.0.1:5173
```

## Testing

```bash
npm run lint
npm test
```

The tests cover dashboard calculations and rendering, accessible tab behavior, Help-to-viewer transitions, PDF navigation and zoom boundaries, viewer recovery and focus behavior, required-field validation, safe URL handling, URL normalization, all supported platform mappings, lookalike-domain rejection, date behavior, automatic applied-date behavior, search, sorting, import validation, merge conflicts, and IndexedDB persistence with `fake-indexeddb`.

## Production Build

```bash
npm run build
```

The production output is written to `dist`.

## Production Preview

```bash
npm run preview
```

Vite preview runs on the fixed port `4173` with `strictPort` enabled.

## IndexedDB Storage

This app stores jobs and settings in IndexedDB through the `idb` package. There is no backend, account system, remote database, analytics, scraping, or job-platform API integration.

Persistence is tied to the current browser profile and origin. Data should remain available after reloads and browser restarts when returning to the same URL in the same browser profile.

Data is not expected to follow you when you:

- Use another browser, profile, device, or private browsing session
- Clear browser or site data
- Switch between localhost and a deployed URL
- Switch between different Vercel preview URLs

Use Export JSON regularly as the backup mechanism.

## Backup and Restore

- **Export** creates a JSON file containing `schemaVersion`, `exportedAt`, `jobs`, and `settings`.
- **Import** accepts local `.json` files only.
- Merge is the default restore path. It preserves existing jobs and skips ID or normalized-URL conflicts.
- Replace requires explicit confirmation and is blocked when the incoming backup contains invalid records.

## Vercel Deployment Readiness

This project is ready for static Vercel hosting. Vercel would host only the frontend files. It would not store jobs, synchronize data, run server functions, or provide authentication.

Git import flow:

1. Push the repository to a Git provider.
2. Import the project in Vercel.
3. Set the project root to `chapter_05_JobTracker/NextGenJobTracker`.
4. Use `npm run build` as the build command.
5. Use `dist` as the output directory.

Vercel CLI flow:

```bash
npm install -g vercel
vercel
vercel --prod
```

Do not deploy from this project without explicit authorization. The included `vercel.json` provides an SPA fallback so refreshed routes resolve to the app.

## Future Authentication Extension Points

Authentication is intentionally not implemented. To add cloud sync later, keep the UI dependent on repository interfaces and replace or wrap:

- `JobRepository`
- `SettingsRepository`
- `IndexedDbJobRepository`
- `IndexedDbSettingsRepository`
- Backup/restore service boundaries

A future authenticated repository could add user-specific cloud storage and synchronization without adding fake login screens or placeholder OAuth code to this local-only version.

## Supported Platforms

The app detects LinkedIn, Naukri, Indeed, Glassdoor, Foundit, Wellfound, Instahyre, Cutshort, Hirist and IIMJobs from safe hostname matching. Unknown valid HTTP/HTTPS URLs are allowed and shown with a generic source badge.
