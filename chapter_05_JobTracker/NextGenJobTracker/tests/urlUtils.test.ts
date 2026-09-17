import { describe, expect, it } from 'vitest';
import {
  hostnameMatchesDomain,
  normalizeHostname,
  normalizeUrlForComparison,
  validateOptionalHttpUrl,
} from '../src/utils/urls';

describe('URL utilities', () => {
  it('accepts only http and https URLs', () => {
    expect(validateOptionalHttpUrl('https://example.com/jobs/1')).toBeUndefined();
    expect(validateOptionalHttpUrl('http://example.com/jobs/1')).toBeUndefined();
    expect(validateOptionalHttpUrl('javascript:alert(1)')).toMatch(/http/);
    expect(validateOptionalHttpUrl('data:text/html,hello')).toMatch(/http/);
    expect(validateOptionalHttpUrl('file:///tmp/job.html')).toMatch(/http/);
    expect(validateOptionalHttpUrl('vbscript:msgbox("x")')).toMatch(/http/);
  });

  it('normalizes URLs for duplicate comparison without dropping job identifiers', () => {
    expect(
      normalizeUrlForComparison(
        ' https://WWW.Example.com/jobs/123/?utm_source=newsletter&trackingId=abc&jobId=42#details ',
      ),
    ).toBe('https://example.com/jobs/123?jobId=42');
  });

  it('matches exact hostnames and genuine subdomains only', () => {
    expect(normalizeHostname('WWW.LinkedIn.com')).toBe('linkedin.com');
    expect(hostnameMatchesDomain('jobs.linkedin.com', 'linkedin.com')).toBe(true);
    expect(hostnameMatchesDomain('linkedin.com', 'linkedin.com')).toBe(true);
    expect(hostnameMatchesDomain('fake-linkedin.com', 'linkedin.com')).toBe(false);
    expect(hostnameMatchesDomain('linkedin.com.attacker.example', 'linkedin.com')).toBe(false);
  });
});
