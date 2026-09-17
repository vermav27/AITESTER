import { SETTINGS_KEY, fromSettingsRecord, getDatabase, toSettingsRecord } from '../db/database';
import type { AppSettings, Job } from '../types/job';
import { DEFAULT_SETTINGS, type JobRepository, type SettingsRepository } from './contracts';

export class IndexedDbJobRepository implements JobRepository {
  async list(): Promise<Job[]> {
    const database = await getDatabase();
    return database.getAll('jobs');
  }

  async save(job: Job): Promise<void> {
    const database = await getDatabase();
    await database.put('jobs', job);
  }

  async saveMany(jobs: Job[]): Promise<void> {
    const database = await getDatabase();
    const transaction = database.transaction('jobs', 'readwrite');
    await Promise.all([...jobs.map((job) => transaction.store.put(job)), transaction.done]);
  }

  async delete(id: string): Promise<void> {
    const database = await getDatabase();
    await database.delete('jobs', id);
  }

  async mergeNew(jobs: Job[]): Promise<number> {
    const database = await getDatabase();
    const transaction = database.transaction('jobs', 'readwrite');
    for (const job of jobs) {
      await transaction.store.add(job);
    }
    await transaction.done;
    return jobs.length;
  }

  async replaceAll(jobs: Job[]): Promise<number> {
    const database = await getDatabase();
    const transaction = database.transaction('jobs', 'readwrite');
    await transaction.store.clear();
    for (const job of jobs) {
      await transaction.store.put(job);
    }
    await transaction.done;
    return jobs.length;
  }
}

export class IndexedDbSettingsRepository implements SettingsRepository {
  async get(): Promise<AppSettings> {
    const database = await getDatabase();
    const record = await database.get('settings', SETTINGS_KEY);
    return record ? fromSettingsRecord(record) : DEFAULT_SETTINGS;
  }

  async save(settings: AppSettings): Promise<void> {
    const database = await getDatabase();
    await database.put('settings', toSettingsRecord(settings));
  }
}
