import { JOB_STATUS_IDS, isAppliedOrLater, isJobStatus, type JobStatus } from '../constants/statuses';
import type { FieldErrors, Job, JobDraft, SortMode } from '../types/job';
import { applyAutomaticAppliedDate, isFutureLocalDate, isValidLocalDate, todayLocalDate } from '../utils/dates';
import { normalizeUrlForComparison, validateOptionalHttpUrl } from '../utils/urls';

export function createEmptyDraft(): JobDraft {
  return {
    companyName: '',
    role: '',
    jobUrl: '',
    resumeName: '',
    appliedDate: '',
    salaryRange: '',
    notes: '',
    status: 'wishlist',
  };
}

export function jobToDraft(job: Job): JobDraft {
  return {
    companyName: job.companyName,
    role: job.role,
    jobUrl: job.jobUrl ?? '',
    resumeName: job.resumeName ?? '',
    appliedDate: job.appliedDate ?? '',
    salaryRange: job.salaryRange ?? '',
    notes: job.notes ?? '',
    status: job.status,
  };
}

export function validateJobDraft(draft: JobDraft, now = new Date()): FieldErrors {
  const errors: FieldErrors = {};
  if (!draft.companyName.trim()) {
    errors.companyName = 'Company name is required.';
  }
  if (!draft.role.trim()) {
    errors.role = 'Role is required.';
  }
  const urlError = validateOptionalHttpUrl(draft.jobUrl);
  if (urlError) {
    errors.jobUrl = urlError;
  }
  if (!isJobStatus(draft.status)) {
    errors.status = 'Choose a supported status.';
  }
  if (draft.appliedDate.trim()) {
    if (!isValidLocalDate(draft.appliedDate.trim())) {
      errors.appliedDate = 'Use a valid date in YYYY-MM-DD format.';
    } else if (isFutureLocalDate(draft.appliedDate.trim(), now)) {
      errors.appliedDate = 'Applied date cannot be in the future.';
    }
  }
  return errors;
}

export function hasFieldErrors(errors: FieldErrors): boolean {
  return Object.keys(errors).length > 0;
}

export function buildJobFromDraft(
  draft: JobDraft,
  existing: Job | null,
  nextPosition: number,
  now = new Date(),
): Job {
  const timestamp = now.toISOString();
  const appliedDate = draft.appliedDate.trim() || (isAppliedOrLater(draft.status) ? todayLocalDate(now) : '');

  return {
    id: existing?.id ?? crypto.randomUUID(),
    companyName: draft.companyName.trim(),
    role: draft.role.trim(),
    jobUrl: draft.jobUrl.trim() || undefined,
    resumeName: draft.resumeName.trim() || undefined,
    appliedDate: appliedDate || null,
    salaryRange: draft.salaryRange.trim() || undefined,
    notes: draft.notes.trim() || undefined,
    status: draft.status,
    position: existing?.position ?? nextPosition,
    createdAt: existing?.createdAt ?? timestamp,
    updatedAt: timestamp,
  };
}

export function prepareStatusChange(job: Job, nextStatus: JobStatus, now = new Date()): Job {
  return {
    ...job,
    status: nextStatus,
    appliedDate: applyAutomaticAppliedDate(job, nextStatus, now),
    updatedAt: now.toISOString(),
  };
}

export function findDuplicateByUrl(draftUrl: string, jobs: Job[], editingId?: string): Job | null {
  const normalizedDraftUrl = normalizeUrlForComparison(draftUrl);
  if (!normalizedDraftUrl) {
    return null;
  }

  return (
    jobs.find((job) => {
      if (job.id === editingId || !job.jobUrl) {
        return false;
      }
      return normalizeUrlForComparison(job.jobUrl) === normalizedDraftUrl;
    }) ?? null
  );
}

export function searchJobs(jobs: Job[], query: string): Job[] {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return jobs;
  }

  return jobs.filter((job) => {
    return (
      job.companyName.toLowerCase().includes(normalized) ||
      job.role.toLowerCase().includes(normalized)
    );
  });
}

export function sortJobsForColumn(jobs: Job[], sortMode: SortMode): Job[] {
  const list = [...jobs];
  if (sortMode === 'manual') {
    return list.sort((a, b) => a.position - b.position || a.createdAt.localeCompare(b.createdAt));
  }

  return list.sort((a, b) => {
    if (!a.appliedDate && !b.appliedDate) {
      return a.createdAt.localeCompare(b.createdAt);
    }
    if (!a.appliedDate) {
      return 1;
    }
    if (!b.appliedDate) {
      return -1;
    }
    const comparison = a.appliedDate.localeCompare(b.appliedDate);
    return sortMode === 'newest' ? -comparison : comparison;
  });
}

export function getNextPosition(jobs: Job[]): number {
  const max = jobs.reduce((highest, job) => Math.max(highest, job.position), 0);
  return max + 1000;
}

export function withRepositionedColumn(jobs: Job[], status: JobStatus): Job[] {
  return jobs.map((job, index) => ({
    ...job,
    status,
    position: (index + 1) * 1000,
    updatedAt: new Date().toISOString(),
  }));
}

export function isKnownStatusId(value: string): value is JobStatus {
  return JOB_STATUS_IDS.includes(value as JobStatus);
}
