export const JOB_STATUSES = [
  { id: 'wishlist', label: 'Wishlist', accent: 'bg-slate-400' },
  { id: 'applied', label: 'Applied', accent: 'bg-sky-500' },
  { id: 'follow-up', label: 'Follow-up', accent: 'bg-amber-500' },
  { id: 'interview', label: 'Interview', accent: 'bg-violet-500' },
  { id: 'offer', label: 'Offer', accent: 'bg-emerald-500' },
  { id: 'rejected', label: 'Rejected', accent: 'bg-rose-500' },
] as const;

export type JobStatus = (typeof JOB_STATUSES)[number]['id'];

export const JOB_STATUS_IDS = JOB_STATUSES.map((status) => status.id) as JobStatus[];

export function isJobStatus(value: unknown): value is JobStatus {
  return typeof value === 'string' && JOB_STATUS_IDS.includes(value as JobStatus);
}

export function getStatusLabel(status: JobStatus): string {
  return JOB_STATUSES.find((item) => item.id === status)?.label ?? status;
}

export function isAppliedOrLater(status: JobStatus): boolean {
  return status !== 'wishlist';
}
