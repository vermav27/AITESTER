import { isAppliedOrLater, type JobStatus } from '../constants/statuses';
import type { Job } from '../types/job';

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const DAY_IN_MS = 24 * 60 * 60 * 1000;

export function todayLocalDate(date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function parseLocalDate(value: string): Date | null {
  if (!DATE_PATTERN.test(value)) {
    return null;
  }

  const [year, month, day] = value.split('-').map(Number);
  const parsed = new Date(year, month - 1, day);

  if (
    parsed.getFullYear() !== year ||
    parsed.getMonth() !== month - 1 ||
    parsed.getDate() !== day
  ) {
    return null;
  }

  return parsed;
}

export function isValidLocalDate(value: string): boolean {
  return parseLocalDate(value) !== null;
}

export function isFutureLocalDate(value: string, now = new Date()): boolean {
  const parsed = parseLocalDate(value);
  if (!parsed) {
    return false;
  }

  const today = parseLocalDate(todayLocalDate(now));
  return today ? parsed.getTime() > today.getTime() : false;
}

export function daysSinceApplied(appliedDate: string | null, now = new Date()): number | null {
  if (!appliedDate) {
    return null;
  }

  const applied = parseLocalDate(appliedDate);
  const today = parseLocalDate(todayLocalDate(now));
  if (!applied || !today) {
    return null;
  }

  return Math.max(0, Math.floor((today.getTime() - applied.getTime()) / DAY_IN_MS));
}

export function formatAppliedAge(appliedDate: string | null, now = new Date()): string {
  const days = daysSinceApplied(appliedDate, now);
  if (days === null) {
    return 'Not applied';
  }
  if (days === 0) {
    return 'Applied today';
  }
  if (days === 1) {
    return '1 day since applied';
  }
  return `${days} days since applied`;
}

export function applyAutomaticAppliedDate(
  job: Pick<Job, 'status' | 'appliedDate'>,
  nextStatus: JobStatus,
  now = new Date(),
): string | null {
  if (job.appliedDate) {
    return job.appliedDate;
  }

  if (job.status === 'wishlist' && isAppliedOrLater(nextStatus)) {
    return todayLocalDate(now);
  }

  return null;
}

export function defaultAppliedDateForStatus(status: JobStatus, providedDate: string, now = new Date()): string {
  if (providedDate) {
    return providedDate;
  }
  return isAppliedOrLater(status) ? todayLocalDate(now) : '';
}
