import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../src/App';
import {
  DATABASE_NAME,
  closeDatabaseConnectionForTests,
  resetDatabaseConnectionForTests,
} from '../src/db/database';
import { DEFAULT_SETTINGS } from '../src/repositories/contracts';
import { IndexedDbSettingsRepository } from '../src/repositories/indexedDb';

function deleteDatabase(name: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.deleteDatabase(name);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
    request.onblocked = () => reject(new Error('Database deletion was blocked.'));
  });
}

describe('application tabs', () => {
  beforeEach(async () => {
    await closeDatabaseConnectionForTests();
    await deleteDatabase(DATABASE_NAME);
    resetDatabaseConnectionForTests();
    await new IndexedDbSettingsRepository().save({ ...DEFAULT_SETTINGS, hasSeenGuide: true });

    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
      callback(0);
      return 1;
    });
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    await closeDatabaseConnectionForTests();
  });

  it('opens on Dashboard and preserves board search while switching views', async () => {
    const user = userEvent.setup();
    render(<App />);

    const dashboardTab = await screen.findByRole('tab', { name: 'Dashboard' });
    const boardTab = screen.getByRole('tab', { name: 'Job Tracker Board' });
    expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tabpanel', { name: 'Dashboard' })).toBeVisible();

    await user.click(boardTab);
    const search = screen.getByRole('textbox', { name: 'Search company and role' });
    await user.type(search, 'Acme');
    expect(boardTab).toHaveAttribute('aria-selected', 'true');

    await user.click(dashboardTab);
    await user.click(boardTab);
    expect(screen.getByRole('textbox', { name: 'Search company and role' })).toHaveValue('Acme');
  });

  it('switches and focuses tabs with horizontal arrow keys', async () => {
    const user = userEvent.setup();
    render(<App />);

    const dashboardTab = await screen.findByRole('tab', { name: 'Dashboard' });
    dashboardTab.focus();
    await user.keyboard('{ArrowRight}');

    const boardTab = screen.getByRole('tab', { name: 'Job Tracker Board' });
    await waitFor(() => expect(boardTab).toHaveFocus());
    expect(boardTab).toHaveAttribute('aria-selected', 'true');
  });
});
