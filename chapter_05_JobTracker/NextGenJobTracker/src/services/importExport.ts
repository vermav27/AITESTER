import { isJobStatus } from '../constants/statuses';
import { isSortMode, isThemePreference } from '../repositories/contracts';
import type { AppSettings, Job } from '../types/job';
import { isFutureLocalDate, isValidLocalDate } from '../utils/dates';
import { normalizeUrlForComparison, validateOptionalHttpUrl } from '../utils/urls';

export const BACKUP_SCHEMA_VERSION = 1;

export interface BackupFile {
  schemaVersion: typeof BACKUP_SCHEMA_VERSION;
  exportedAt: string;
  jobs: Job[];
  settings: AppSettings;
}

export interface InvalidImportRecord {
  index: number;
  reason: string;
}

export interface ImportConflict {
  index: number;
  incoming: Job;
  existing: Job;
  reason: 'id' | 'url';
}

interface ValidImportEntry {
  index: number;
  job: Job;
}

export interface ImportPlan {
  schemaVersion: number;
  exportedAt: string;
  settings: AppSettings;
  validJobs: Job[];
  importableJobs: Job[];
  invalidRecords: InvalidImportRecord[];
  conflicts: ImportConflict[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isIsoDate(value: string): boolean {
  const parsed = new Date(value);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString() === value;
}

function optionalString(record: Record<string, unknown>, key: keyof Job): string | undefined | false {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  return typeof value === 'string' ? value : false;
}

export function validateImportedJob(value: unknown, index: number, now = new Date()): Job | InvalidImportRecord {
  if (!isRecord(value)) {
    return { index, reason: 'Record is not an object.' };
  }

  const requiredStringKeys = ['id', 'companyName', 'role', 'createdAt', 'updatedAt'] as const;
  for (const key of requiredStringKeys) {
    if (typeof value[key] !== 'string' || !value[key].trim()) {
      return { index, reason: `${key} must be a non-empty string.` };
    }
  }

  const status = value.status;
  if (!isJobStatus(status)) {
    return { index, reason: 'status is not supported.' };
  }

  if (typeof value.position !== 'number' || !Number.isFinite(value.position)) {
    return { index, reason: 'position must be a finite number.' };
  }

  if (!('appliedDate' in value)) {
    return { index, reason: 'appliedDate is missing.' };
  }

  if (value.appliedDate !== null) {
    if (typeof value.appliedDate !== 'string' || !isValidLocalDate(value.appliedDate)) {
      return { index, reason: 'appliedDate must be YYYY-MM-DD or null.' };
    }
    if (isFutureLocalDate(value.appliedDate, now)) {
      return { index, reason: 'appliedDate cannot be in the future.' };
    }
  }

  const id = value.id;
  const companyName = value.companyName;
  const role = value.role;
  const createdAt = value.createdAt;
  const updatedAt = value.updatedAt;

  if (
    typeof id !== 'string' ||
    typeof companyName !== 'string' ||
    typeof role !== 'string' ||
    typeof createdAt !== 'string' ||
    typeof updatedAt !== 'string' ||
    !isIsoDate(createdAt) ||
    !isIsoDate(updatedAt)
  ) {
    return { index, reason: 'createdAt and updatedAt must be ISO timestamps.' };
  }

  const jobUrl = optionalString(value, 'jobUrl');
  const resumeName = optionalString(value, 'resumeName');
  const salaryRange = optionalString(value, 'salaryRange');
  const notes = optionalString(value, 'notes');
  if (jobUrl === false || resumeName === false || salaryRange === false || notes === false) {
    return { index, reason: 'Optional text fields must be strings when present.' };
  }

  if (jobUrl && validateOptionalHttpUrl(jobUrl)) {
    return { index, reason: 'jobUrl must be http:// or https://.' };
  }

  return {
    id: id.trim(),
    companyName: companyName.trim(),
    role: role.trim(),
    jobUrl: jobUrl?.trim() || undefined,
    resumeName: resumeName?.trim() || undefined,
    appliedDate: value.appliedDate,
    salaryRange: salaryRange?.trim() || undefined,
    notes: notes?.trim() || undefined,
    status,
    position: value.position,
    createdAt,
    updatedAt,
  };
}

export function validateImportedSettings(value: unknown): AppSettings {
  if (!isRecord(value)) {
    throw new Error('Backup settings must be an object.');
  }

  if (
    !isThemePreference(value.theme) ||
    !isSortMode(value.sortMode) ||
    typeof value.hasSeenGuide !== 'boolean'
  ) {
    throw new Error('Backup settings contain unsupported values.');
  }

  return {
    theme: value.theme,
    sortMode: value.sortMode,
    hasSeenGuide: value.hasSeenGuide,
  };
}

export function parseBackupJson(raw: string): unknown {
  return JSON.parse(raw) as unknown;
}

export function buildBackup(jobs: Job[], settings: AppSettings): BackupFile {
  return {
    schemaVersion: BACKUP_SCHEMA_VERSION,
    exportedAt: new Date().toISOString(),
    jobs,
    settings,
  };
}

export function getBackupFilename(date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `job-tracker-backup-${year}-${month}-${day}.json`;
}

export function createImportPlan(input: unknown, existingJobs: Job[], now = new Date()): ImportPlan {
  if (!isRecord(input)) {
    throw new Error('Backup must be a JSON object.');
  }

  if (input.schemaVersion !== BACKUP_SCHEMA_VERSION) {
    throw new Error('Unsupported backup schema version.');
  }

  if (typeof input.exportedAt !== 'string' || !isIsoDate(input.exportedAt)) {
    throw new Error('Backup exportedAt must be an ISO timestamp.');
  }

  const rawJobs = input.jobs;
  if (!Array.isArray(rawJobs)) {
    throw new Error('Backup jobs must be an array.');
  }

  const validEntries: ValidImportEntry[] = [];
  const invalidRecords: InvalidImportRecord[] = [];
  const incomingIds = new Map<string, number>();
  const incomingUrls = new Map<string, number>();

  rawJobs.forEach((record, index) => {
    const result = validateImportedJob(record, index, now);
    if ('reason' in result) {
      invalidRecords.push(result);
      return;
    }

    const previousIdIndex = incomingIds.get(result.id);
    if (previousIdIndex !== undefined) {
      invalidRecords.push({
        index,
        reason: `Duplicate id inside backup; first seen at record #${previousIdIndex + 1}.`,
      });
      return;
    }

    const normalizedUrl = result.jobUrl ? normalizeUrlForComparison(result.jobUrl) : null;
    if (normalizedUrl) {
      const previousUrlIndex = incomingUrls.get(normalizedUrl);
      if (previousUrlIndex !== undefined) {
        invalidRecords.push({
          index,
          reason: `Duplicate normalized URL inside backup; first seen at record #${previousUrlIndex + 1}.`,
        });
        return;
      }
      incomingUrls.set(normalizedUrl, index);
    }

    incomingIds.set(result.id, index);
    validEntries.push({ index, job: result });
  });

  const validJobs = validEntries.map((entry) => entry.job);

  const conflicts: ImportConflict[] = [];
  const importableJobs: Job[] = [];
  const existingById = new Map(existingJobs.map((job) => [job.id, job]));
  const existingByUrl = new Map<string, Job>();

  for (const job of existingJobs) {
    if (job.jobUrl) {
      const normalized = normalizeUrlForComparison(job.jobUrl);
      if (normalized) {
        existingByUrl.set(normalized, job);
      }
    }
  }

  validEntries.forEach(({ job, index }) => {
    const idConflict = existingById.get(job.id);
    if (idConflict) {
      conflicts.push({ index, incoming: job, existing: idConflict, reason: 'id' });
      return;
    }

    const normalizedUrl = job.jobUrl ? normalizeUrlForComparison(job.jobUrl) : null;
    const urlConflict = normalizedUrl ? existingByUrl.get(normalizedUrl) : undefined;
    if (urlConflict) {
      conflicts.push({ index, incoming: job, existing: urlConflict, reason: 'url' });
      return;
    }

    importableJobs.push(job);
  });

  return {
    schemaVersion: input.schemaVersion,
    exportedAt: input.exportedAt,
    settings: validateImportedSettings(input.settings),
    validJobs,
    importableJobs,
    invalidRecords,
    conflicts,
  };
}
