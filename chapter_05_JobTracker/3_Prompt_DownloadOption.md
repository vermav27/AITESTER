# RICEPOT Framework: View-Only User Guide and Documentation Updates

## R - Role

Act as a senior React/TypeScript engineer, accessibility specialist, security-aware product designer, documentation author, and careful Git maintainer. Implement the viewer while keeping the local-first architecture, shared modal behavior, responsive UI, and project documentation consistent.

## I - Instructions

- Create `chapter_05_JobTracker/3_Prompt_DownloadOption.md` containing this approved RICEPOT plan.
- Add **View User Guide** beside **How to use this tracker** in the Help popup.
- Open the PDF in a dedicated in-app PDF.js viewer.
- Expose no Download, Print, Open in New Tab, or direct-file-link controls.
- Provide page navigation, zoom, loading, retry, and Back to Help controls.
- Update `Architecture/Architecture.png` to include the Dashboard and PDF viewer architecture.
- Regenerate `Architecture/NextGenJobTracker_User_Guide.pdf` with the new Help/viewer experience.
- Keep exactly one PNG in the Architecture folder.
- Do not push or deploy without separate authorization.

## C - Context

- The current Help popup uses the shared `Modal` component.
- `pdfjs-dist` is not installed and will become a production dependency.
- The existing guide is a five-page PDF and will remain five pages.
- The existing architecture image predates the Dashboard and user-guide viewer.
- The application is a static Vite frontend with no authentication or protected document server.
- Removing download controls discourages casual downloading but cannot guarantee that browser-delivered content is unrecoverable.

## E - Expected Success Criteria

### Viewer

- Help displays **View User Guide** next to the title on desktop and wraps cleanly on tablet layouts.
- Clicking it replaces the Help modal with a larger viewer modal; dialogs are never stacked.
- The viewer opens on page 1 and dynamically reports the PDF's five-page count.
- Previous and Next respect first/last-page boundaries.
- Zoom Out, Reset Zoom, and Zoom In operate within 75%-175%.
- PDF pages render sharply and responsively without horizontal page overflow.
- No download, print, native browser toolbar, or raw PDF link appears.
- Close or Escape returns to Help; closing Help returns focus to its original launcher.
- Loading and rendering failures show Retry and Back to Help.
- Light, Dark, and System themes remain aligned and readable.

### Architecture

- Preserve the existing clean blue/green layered architecture style.
- Update the Presentation Layer with:
  - App Shell & Tabs
  - Dashboard
  - Kanban Board
  - Job Cards
  - Forms & Dialogs
  - Theme & Help
  - User Guide Viewer
- Update Application Services with Dashboard Metrics and PDF.js Rendering.
- Add a labeled flow from Help to PDF.js Rendering to the bundled User Guide PDF.
- Keep JSON backup, IndexedDB, repositories, platform registry, and local-first boundaries intact.
- Add PDF.js to the technology row.
- Replace the current `Architecture.png` only after text and layout validation.

### User Guide

- Keep the guide at five A4 pages.
- Preserve Dashboard, Kanban, Add Job, search, backup, theme, and local-storage guidance.
- Update screenshots after implementation.
- Add the Help-to-Viewer workflow and viewer controls.
- State that the UI provides viewing without download or print controls.
- Keep the guide readable, unclipped, and free of personal job data.

## P - Parameters and Interfaces

### Modal API

Extend the shared modal interface backward-compatibly:

```ts
interface ModalProps {
  headerAction?: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}
```

Existing modal consumers retain their current layout and default size.

### PDF Viewer

- Add `pdfjs-dist` and lock the installed version.
- Load PDF.js lazily when the viewer opens.
- Configure the PDF.js worker through a Vite-compatible worker URL.
- Resolve the guide through Vite from:
  ```ts
  ../../Architecture/NextGenJobTracker_User_Guide.pdf
  ```
- Use an internal interface:
  ```ts
  interface UserGuideViewerProps {
    pdfUrl: string;
    onBack: () => void;
  }
  ```
- Render one page at a time to canvas using container width and device-pixel ratio.
- Extract page text into a visually hidden description for screen-reader access.
- Cancel stale loading/render tasks after page, zoom, size, or lifecycle changes.
- Do not use an iframe, `<object>`, download anchor, Blob download, browser print API, or external document service.

### Modal Transition

- `HelpGuide` owns a Help/Viewer view state.
- Help and Viewer render conditionally so only one dialog exists.
- **View User Guide** switches to the viewer.
- Viewer Close, Escape, and Back switch back to Help.
- Final Help Close dismisses the overall experience.

### Documentation Assets

- Use the existing `Architecture.png` as the image-edit target through the built-in image editing workflow.
- Preserve the title, local-first message, existing architecture layers, and 16:9 landscape composition.
- Use fresh Playwright screenshots for the updated PDF.
- Keep temporary screenshots and PDF-generation HTML under ignored `test-results`.
- Overwrite only the approved final PNG and PDF after visual verification.

## O - Output

- `chapter_05_JobTracker/3_Prompt_DownloadOption.md`
- Updated Help popup and shared Modal
- New in-app PDF.js viewer
- Updated package manifest and lockfile
- Updated `Architecture/Architecture.png`
- Updated `Architecture/NextGenJobTracker_User_Guide.pdf`
- Focused automated viewer tests
- Updated README and append-only session log
- One or more logical local commits
- No push or deployment

## T - Tasks

1. Save this approved framework in `3_Prompt_DownloadOption.md`.
2. Install and inspect the resolved `pdfjs-dist` API.
3. Extend Modal with header action and `xl` size.
4. Implement non-stacked Help-to-Viewer transitions.
5. Implement PDF loading, canvas rendering, text extraction, navigation, zoom, retry, and cleanup.
6. Add component tests with mocked PDF.js and canvas behavior.
7. Verify no download, print, raw-link, or browser-toolbar controls render.
8. Run lint, all tests, and the production build.
9. Confirm the built output contains the PDF and PDF.js worker.
10. Run headed Chromium checks at desktop and tablet widths in light and dark themes.
11. Navigate all pages, exercise zoom boundaries, and check nonblank canvas pixels.
12. Capture clean Help and viewer screenshots.
13. Edit `Architecture.png`, preserving existing visual invariants and adding the new viewer flow.
14. Regenerate the five-page user guide with the new screenshots and instructions.
15. Confirm the PDF is exactly five pages and visually inspect every page.
16. Confirm Architecture contains exactly one PNG and one PDF.
17. Update README and append the verified results to the session log.
18. Review the diff, preserve unrelated files, and create logical local commits.

## Assumptions and Limitations

- The confirmed prompt path is `chapter_05_JobTracker/3_Prompt_DownloadOption.md`.
- **View User Guide** replaces the previously proposed download action.
- The guide remains five pages to preserve the earlier four-to-five-page requirement.
- The viewer provides no download capability in its UI.
- Absolute prevention remains impossible in a static browser application because users can inspect network data, caches, or screenshots.
