import { beforeEach, describe, expect, it } from 'vitest';
import {
  DATABASE_NAME,
  closeDatabaseConnectionForTests,
  resetDatabaseConnectionForTests,
} from '../src/db/database';
import { DEFAULT_SETTINGS } from '../src/repositories/contracts';
import { IndexedDbJobRepository, IndexedDbSettingsRepository } from '../src/repositories/indexedDb';
import { replaceDatabaseContents } from '../src/repositories/backupRepository';
import { makeJob } from './testHelpers';

function deleteDatabase(name: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.deleteDatabase(name);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
    request.onblocked = () => reject(new Error('Database deletion was blocked.'));
  });
}

describe('IndexedDB repositories', () => {
  beforeEach(async () => {
    await closeDatabaseConnectionForTests();
    await deleteDatabase(DATABASE_NAME);
    resetDatabaseConnectionForTests();
  });

  it('persists jobs and settings in IndexedDB', async () => {
    const jobs = new IndexedDbJobRepository();
    const settings = new IndexedDbSettingsRepository();
    const job = makeJob({ id: 'job-1', companyName: 'Persisted' });

    await jobs.save(job);
    await settings.save({ ...DEFAULT_SETTINGS, theme: 'dark', hasSeenGuide: true });

    await expect(jobs.list()).resolves.toEqual([job]);
    await expect(settings.get()).resolves.toEqual({ ...DEFAULT_SETTINGS, theme: 'dark', hasSeenGuide: true });
  });

  it('merges new records and replaces database contents transactionally', async () => {
    const jobs = new IndexedDbJobRepository();
    const first = makeJob({ id: 'first' });
    const second = makeJob({ id: 'second' });
    const replacement = makeJob({ id: 'replacement' });

    await jobs.mergeNew([first, second]);
    expect(await jobs.list()).toHaveLength(2);

    await replaceDatabaseContents([replacement], { ...DEFAULT_SETTINGS, sortMode: 'newest' });
    expect((await jobs.list()).map((job) => job.id)).toEqual(['replacement']);
    await expect(new IndexedDbSettingsRepository().get()).resolves.toEqual({
      ...DEFAULT_SETTINGS,
      sortMode: 'newest',
    });
  });

  it('deletes persisted jobs', async () => {
    const jobs = new IndexedDbJobRepository();
    await jobs.save(makeJob({ id: 'delete-me' }));
    await jobs.delete('delete-me');
    expect(await jobs.list()).toEqual([]);
  });
});
