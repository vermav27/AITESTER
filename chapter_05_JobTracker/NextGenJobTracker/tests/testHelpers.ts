import type { Job } from '../src/types/job';

export function makeJob(overrides: Partial<Job> = {}): Job {
  return {
    id: overrides.id ?? crypto.randomUUID(),
    companyName: overrides.companyName ?? 'Acme',
    role: overrides.role ?? 'QA Engineer',
    jobUrl: overrides.jobUrl,
    resumeName: overrides.resumeName,
    appliedDate: overrides.appliedDate ?? null,
    salaryRange: overrides.salaryRange,
    notes: overrides.notes,
    status: overrides.status ?? 'wishlist',
    position: overrides.position ?? 1000,
    createdAt: overrides.createdAt ?? '2026-09-01T00:00:00.000Z',
    updatedAt: overrides.updatedAt ?? '2026-09-01T00:00:00.000Z',
  };
}
