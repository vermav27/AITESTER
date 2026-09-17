import { describe, expect, it } from 'vitest';
import {
  buildJobFromDraft,
  createEmptyDraft,
  findDuplicateByUrl,
  searchJobs,
  sortJobsForColumn,
  validateJobDraft,
} from '../src/services/jobLogic';
import { makeJob } from './testHelpers';

describe('job logic', () => {
  it('validates required fields, safe URLs and future dates', () => {
    const errors = validateJobDraft({
      ...createEmptyDraft(),
      companyName: '   ',
      role: '',
      jobUrl: 'javascript:alert(1)',
      appliedDate: '2026-09-18',
    }, new Date(2026, 8, 17));

    expect(errors.companyName).toBeDefined();
    expect(errors.role).toBeDefined();
    expect(errors.jobUrl).toBeDefined();
    expect(errors.appliedDate).toBeDefined();
  });

  it('defaults applied date when creating directly in a later status', () => {
    const draft = {
      ...createEmptyDraft(),
      companyName: 'Acme',
      role: 'SDET',
      status: 'interview' as const,
    };

    const job = buildJobFromDraft(draft, null, 2000, new Date(2026, 8, 17, 10));
    expect(job.appliedDate).toBe('2026-09-17');
    expect(job.position).toBe(2000);
  });

  it('finds duplicate jobs by normalized URL without blocking unknown query identifiers', () => {
    const existing = makeJob({
      id: 'existing',
      companyName: 'Acme',
      role: 'QA',
      jobUrl: 'https://example.com/jobs/1?jobId=42&utm_source=a#top',
    });

    expect(findDuplicateByUrl('https://www.example.com/jobs/1/?jobId=42', [existing])?.id).toBe('existing');
    expect(findDuplicateByUrl('https://example.com/jobs/1?jobId=43', [existing])).toBeNull();
  });

  it('searches company and role case-insensitively', () => {
    const jobs = [
      makeJob({ companyName: 'Northwind', role: 'Frontend Engineer' }),
      makeJob({ companyName: 'Globex', role: 'QA Lead' }),
    ];

    expect(searchJobs(jobs, ' front ')).toHaveLength(1);
    expect(searchJobs(jobs, 'GLOBEX')).toHaveLength(1);
  });

  it('sorts by manual position and date modes with undated jobs last', () => {
    const jobs = [
      makeJob({ id: 'a', position: 3000, appliedDate: null }),
      makeJob({ id: 'b', position: 1000, appliedDate: '2026-09-10' }),
      makeJob({ id: 'c', position: 2000, appliedDate: '2026-09-12' }),
    ];

    expect(sortJobsForColumn(jobs, 'manual').map((job) => job.id)).toEqual(['b', 'c', 'a']);
    expect(sortJobsForColumn(jobs, 'newest').map((job) => job.id)).toEqual(['c', 'b', 'a']);
    expect(sortJobsForColumn(jobs, 'oldest').map((job) => job.id)).toEqual(['b', 'c', 'a']);
  });
});
