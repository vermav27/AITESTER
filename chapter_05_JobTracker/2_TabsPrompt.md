# Approved RICEPOT Plan: Dashboard and Board Tabs

## R — Role

Implement the approved dashboard as a senior React/TypeScript engineer and product designer while preserving accessibility, IndexedDB persistence, responsive behavior, dark mode, and existing Kanban workflows.

## I — Instructions

- Create `chapter_05_JobTracker/2_TabsPrompt.md` containing this approved RICEPOT plan.
- Add **Dashboard** and **Job Tracker Board** tabs.
- Open Dashboard by default without persisting the selected tab.
- Keep the existing Kanban setup inside Job Tracker Board.
- Show seven colorful metric cards for total jobs and all six statuses.
- Add an accessible donut chart and proportional status bars.
- Add green Offer and red Rejected columns containing company name and role.
- Sort those outcome lists by `updatedAt`, newest first.
- Preserve global Help, Export, Import, Add Job, and Theme controls.
- Show Search and Sort only on the board.

## C — Context

- Derive all Dashboard content from the existing top-level `jobs` state.
- Update metrics and outcome lists immediately after any job mutation or import.
- Preserve existing status IDs, repository contracts, backup format, and IndexedDB schema.
- Add no backend, remote storage, analytics, authentication, or chart dependency.
- Preserve unrelated working-tree files.

## E — Expected Success Criteria

- Tabs are accessible by keyboard, mouse, and touch and expose correct ARIA semantics.
- Tab switching preserves board search and sorting state.
- Metric totals are accurate and unaffected by board search.
- The graph provides labels, counts, and percentages without relying only on color.
- Empty data produces zero-valued cards, a neutral chart, and helpful empty states.
- Offer and Rejected sections show all matching jobs with company and role.
- Offer has accessible green styling; Rejected has accessible red styling.
- Outcome entries use newest-updated ordering and a company-name tie-breaker.
- The dashboard and board remain aligned without horizontal page overflow.
- Light and dark themes remain readable and professional.

## P — Parameters

- Add local `AppView = 'dashboard' | 'board'` state initialized to `dashboard`.
- Add a `Dashboard` component accepting `jobs: Job[]`.
- Add a pure aggregation utility for totals, percentages, and outcome lists.
- Use semantic tab roles and associated tab panels.
- Use native responsive SVG and CSS for the chart.
- Use Lucide icons and the existing multi-color status palette.
- Use responsive metric grids and two equal outcome columns that stack on narrower screens.
- Keep Offer and Rejected as standalone sections with list rows, avoiding nested cards.
- Do not alter persisted records or introduce database migrations.

## O — Output

- `chapter_05_JobTracker/2_TabsPrompt.md`
- Accessible application tabs
- Dashboard metrics and visualization
- Offer and Rejected outcome columns
- Preserved Kanban board
- Automated calculation and component tests
- Updated README and append-only session log
- One verified local commit
- No push or deployment

## T — Tasks

1. Create `2_TabsPrompt.md` with the approved plan.
2. Implement and test the dashboard aggregation utility.
3. Build the seven metric cards.
4. Build the SVG donut and proportional status bars.
5. Build the Offer and Rejected company sections.
6. Add accessible tabs and contextual board controls.
7. Preserve all existing board workflows and state.
8. Add tests for calculations, ordering, empty states, rendering, and tab interaction.
9. Run lint, all automated tests, and the production build.
10. Run headed visual checks across desktop and tablet widths in light and dark themes.
11. Verify live updates, long content, overflow, alignment, keyboard behavior, and console output.
12. Update README and append verified results to the session log.
13. Review the diff and create a logical local commit.
