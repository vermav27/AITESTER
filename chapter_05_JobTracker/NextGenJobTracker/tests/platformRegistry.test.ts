import { describe, expect, it } from 'vitest';
import { detectPlatform } from '../src/platforms/registry';

describe('platform registry', () => {
  it.each([
    ['https://www.linkedin.com/jobs/view/1', 'LinkedIn'],
    ['https://jobs.linkedin.com/view/1', 'LinkedIn'],
    ['https://lnkd.in/abc', 'LinkedIn'],
    ['https://www.naukri.com/job-listings/1', 'Naukri'],
    ['https://in.indeed.com/viewjob?jk=1', 'Indeed'],
    ['https://glassdoor.co.in/job-listing/1', 'Glassdoor'],
    ['https://www.glassdoor.com/job-listing/1', 'Glassdoor'],
    ['https://jobs.foundit.in/job/1', 'Foundit'],
    ['https://wellfound.com/jobs/1', 'Wellfound'],
    ['https://www.instahyre.com/job/1', 'Instahyre'],
    ['https://cutshort.io/job/1', 'Cutshort'],
    ['https://www.hirist.tech/job/1', 'Hirist'],
    ['https://www.iimjobs.com/job/1', 'IIMJobs'],
  ])('detects %s as %s', (url, expectedName) => {
    expect(detectPlatform(url)?.name).toBe(expectedName);
  });

  it('rejects lookalike domains and falls back to the hostname', () => {
    expect(detectPlatform('https://fake-linkedin.com/jobs/1')?.id).toBe('unknown');
    expect(detectPlatform('https://linkedin.com.attacker.example/jobs/1')?.id).toBe('unknown');
  });
});
