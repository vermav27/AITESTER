import { getDatabase, toSettingsRecord } from '../db/database';
import type { AppSettings, Job } from '../types/job';

export async function replaceDatabaseContents(jobs: Job[], settings: AppSettings): Promise<number> {
  const database = await getDatabase();
  const transaction = database.transaction(['jobs', 'settings'], 'readwrite');
  await transaction.objectStore('jobs').clear();
  for (const job of jobs) {
    await transaction.objectStore('jobs').put(job);
  }
  await transaction.objectStore('settings').put(toSettingsRecord(settings));
  await transaction.done;
  return jobs.length;
}
