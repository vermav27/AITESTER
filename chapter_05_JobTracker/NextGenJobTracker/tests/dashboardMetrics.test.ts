import { describe, expect, it } from 'vitest';
import { calculateDashboardMetrics } from '../src/services/dashboardMetrics';
import { makeJob } from './testHelpers';

describe('dashboard metrics', () => {
  it('returns zero values and empty outcomes when no jobs exist', () => {
    const metrics = calculateDashboardMetrics([]);

    expect(metrics.total).toBe(0);
    expect(metrics.statuses).toHaveLength(6);
    expect(metrics.statuses.every((metric) => metric.count === 0 && metric.percentage === 0)).toBe(true);
    expect(metrics.offers).toEqual([]);
    expect(metrics.rejected).toEqual([]);
  });

  it('calculates counts, percentages and the total across every status', () => {
    const jobs = [
      makeJob({ id: 'wishlist', status: 'wishlist' }),
      makeJob({ id: 'applied-1', status: 'applied' }),
      makeJob({ id: 'applied-2', status: 'applied' }),
      makeJob({ id: 'follow-up', status: 'follow-up' }),
      makeJob({ id: 'interview', status: 'interview' }),
      makeJob({ id: 'offer', status: 'offer' }),
      makeJob({ id: 'rejected', status: 'rejected' }),
    ];

    const metrics = calculateDashboardMetrics(jobs);
    const countByStatus = Object.fromEntries(metrics.statuses.map((metric) => [metric.status, metric.count]));

    expect(metrics.total).toBe(7);
    expect(countByStatus).toEqual({
      wishlist: 1,
      applied: 2,
      'follow-up': 1,
      interview: 1,
      offer: 1,
      rejected: 1,
    });
    expect(metrics.statuses.reduce((total, metric) => total + metric.count, 0)).toBe(metrics.total);
    expect(metrics.statuses.find((metric) => metric.status === 'applied')?.percentage).toBe(29);
  });

  it('sorts offer and rejected jobs by updated time with stable company tie-breaking', () => {
    const jobs = [
      makeJob({ id: 'offer-old', status: 'offer', companyName: 'Zeta', updatedAt: '2026-09-10T10:00:00.000Z' }),
      makeJob({ id: 'offer-a', status: 'offer', companyName: 'Alpha', updatedAt: '2026-09-12T10:00:00.000Z' }),
      makeJob({ id: 'offer-b', status: 'offer', companyName: 'Beta', updatedAt: '2026-09-12T10:00:00.000Z' }),
      makeJob({ id: 'rejected-old', status: 'rejected', companyName: 'Earlier', updatedAt: '2026-09-11T10:00:00.000Z' }),
      makeJob({ id: 'rejected-new', status: 'rejected', companyName: 'Latest', updatedAt: '2026-09-13T10:00:00.000Z' }),
    ];

    const metrics = calculateDashboardMetrics(jobs);

    expect(metrics.offers.map((job) => job.id)).toEqual(['offer-a', 'offer-b', 'offer-old']);
    expect(metrics.rejected.map((job) => job.id)).toEqual(['rejected-new', 'rejected-old']);
  });
});
