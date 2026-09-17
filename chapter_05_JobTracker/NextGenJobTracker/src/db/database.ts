import { openDB, type DBSchema, type IDBPDatabase } from 'idb';
import type { AppSettings, Job } from '../types/job';

export const DATABASE_NAME = 'nextgen-job-tracker';
export const DATABASE_VERSION = 1;
export const SETTINGS_KEY = 'app';

interface SettingsRecord extends AppSettings {
  id: typeof SETTINGS_KEY;
}

export interface JobTrackerDatabase extends DBSchema {
  jobs: {
    key: string;
    value: Job;
    indexes: {
      'by-status': string;
      'by-position': number;
      'by-updatedAt': string;
    };
  };
  settings: {
    key: string;
    value: SettingsRecord;
  };
}

let databasePromise: Promise<IDBPDatabase<JobTrackerDatabase>> | null = null;

export function getDatabase(): Promise<IDBPDatabase<JobTrackerDatabase>> {
  databasePromise ??= openDB<JobTrackerDatabase>(DATABASE_NAME, DATABASE_VERSION, {
    upgrade(database) {
      if (!database.objectStoreNames.contains('jobs')) {
        const jobs = database.createObjectStore('jobs', { keyPath: 'id' });
        jobs.createIndex('by-status', 'status');
        jobs.createIndex('by-position', 'position');
        jobs.createIndex('by-updatedAt', 'updatedAt');
      }

      if (!database.objectStoreNames.contains('settings')) {
        database.createObjectStore('settings', { keyPath: 'id' });
      }
    },
  });

  return databasePromise;
}

export function toSettingsRecord(settings: AppSettings): SettingsRecord {
  return { id: SETTINGS_KEY, ...settings };
}

export function fromSettingsRecord(record: SettingsRecord): AppSettings {
  return {
    theme: record.theme,
    sortMode: record.sortMode,
    hasSeenGuide: record.hasSeenGuide,
  };
}

export function resetDatabaseConnectionForTests(): void {
  databasePromise = null;
}

export async function closeDatabaseConnectionForTests(): Promise<void> {
  if (!databasePromise) {
    return;
  }

  const database = await databasePromise;
  database.close();
  databasePromise = null;
}
