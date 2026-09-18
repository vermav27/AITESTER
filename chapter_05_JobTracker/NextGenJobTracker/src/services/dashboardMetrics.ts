import { JOB_STATUSES, type JobStatus } from '../constants/statuses';
import type { Job } from '../types/job';

export interface StatusMetric {
  status: JobStatus;
  label: string;
  count: number;
  percentage: number;
  share: number;
}

export interface DashboardMetrics {
  total: number;
  statuses: StatusMetric[];
  offers: Job[];
  rejected: Job[];
}

function sortByMostRecentlyUpdated(jobs: Job[]): Job[] {
  return [...jobs].sort((left, right) => {
    const updatedDifference = Date.parse(right.updatedAt) - Date.parse(left.updatedAt);
    if (updatedDifference !== 0) {
      return updatedDifference;
    }

    const companyDifference = left.companyName.localeCompare(right.companyName);
    return companyDifference !== 0 ? companyDifference : left.id.localeCompare(right.id);
  });
}

export function calculateDashboardMetrics(jobs: Job[]): DashboardMetrics {
  const counts = new Map<JobStatus, number>(JOB_STATUSES.map((status) => [status.id, 0]));

  for (const job of jobs) {
    counts.set(job.status, (counts.get(job.status) ?? 0) + 1);
  }

  const total = jobs.length;
  const statuses = JOB_STATUSES.map((status) => {
    const count = counts.get(status.id) ?? 0;
    const share = total === 0 ? 0 : (count / total) * 100;

    return {
      status: status.id,
      label: status.label,
      count,
      percentage: Math.round(share),
      share,
    };
  });

  return {
    total,
    statuses,
    offers: sortByMostRecentlyUpdated(jobs.filter((job) => job.status === 'offer')),
    rejected: sortByMostRecentlyUpdated(jobs.filter((job) => job.status === 'rejected')),
  };
}
