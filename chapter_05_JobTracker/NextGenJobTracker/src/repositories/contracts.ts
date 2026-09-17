import type { AppSettings, Job, SortMode, ThemePreference } from '../types/job';

export const DEFAULT_SETTINGS: AppSettings = {
  theme: 'system',
  sortMode: 'manual',
  hasSeenGuide: false,
};

export interface JobRepository {
  list(): Promise<Job[]>;
  save(job: Job): Promise<void>;
  saveMany(jobs: Job[]): Promise<void>;
  delete(id: string): Promise<void>;
  mergeNew(jobs: Job[]): Promise<number>;
  replaceAll(jobs: Job[]): Promise<number>;
}

export interface SettingsRepository {
  get(): Promise<AppSettings>;
  save(settings: AppSettings): Promise<void>;
}

export function isSortMode(value: unknown): value is SortMode {
  return value === 'manual' || value === 'newest' || value === 'oldest';
}

export function isThemePreference(value: unknown): value is ThemePreference {
  return value === 'system' || value === 'light' || value === 'dark';
}
