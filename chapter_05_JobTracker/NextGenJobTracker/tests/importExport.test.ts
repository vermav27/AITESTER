import { describe, expect, it } from 'vitest';
import { BACKUP_SCHEMA_VERSION, buildBackup, createImportPlan } from '../src/services/importExport';
import { DEFAULT_SETTINGS } from '../src/repositories/contracts';
import { makeJob } from './testHelpers';

describe('import and export', () => {
  it('builds backups with schema, timestamp, jobs and settings', () => {
    const backup = buildBackup([makeJob({ id: 'one' })], DEFAULT_SETTINGS);
    expect(backup.schemaVersion).toBe(BACKUP_SCHEMA_VERSION);
    expect(backup.exportedAt).toEqual(expect.any(String));
    expect(backup.jobs).toHaveLength(1);
    expect(backup.settings).toEqual(DEFAULT_SETTINGS);
  });

  it('rejects unsupported schema versions and invalid records', () => {
    expect(() =>
      createImportPlan({ schemaVersion: 999, exportedAt: new Date().toISOString(), jobs: [], settings: DEFAULT_SETTINGS }, []),
    ).toThrow(/Unsupported/);

    const plan = createImportPlan(
      {
        schemaVersion: BACKUP_SCHEMA_VERSION,
        exportedAt: new Date().toISOString(),
        jobs: [{ companyName: 'Missing model fields' }],
        settings: DEFAULT_SETTINGS,
      },
      [],
    );

    expect(plan.invalidRecords).toHaveLength(1);
    expect(plan.importableJobs).toHaveLength(0);
  });

  it('reports matching ID and URL conflicts before writing', () => {
    const existingById = makeJob({ id: 'same-id', companyName: 'Existing ID' });
    const existingByUrl = makeJob({
      id: 'url-job',
      companyName: 'Existing URL',
      jobUrl: 'https://example.com/job/1?utm_source=a',
    });

    const incomingId = makeJob({ id: 'same-id', companyName: 'Incoming ID' });
    const incomingUrl = makeJob({
      id: 'incoming-url',
      companyName: 'Incoming URL',
      jobUrl: 'https://www.example.com/job/1/',
    });
    const importable = makeJob({ id: 'new-job', jobUrl: 'https://example.com/job/2' });

    const plan = createImportPlan(
      {
        schemaVersion: BACKUP_SCHEMA_VERSION,
        exportedAt: new Date().toISOString(),
        jobs: [incomingId, incomingUrl, importable],
        settings: DEFAULT_SETTINGS,
      },
      [existingById, existingByUrl],
    );

    expect(plan.validJobs).toHaveLength(3);
    expect(plan.conflicts.map((conflict) => conflict.reason)).toEqual(['id', 'url']);
    expect(plan.importableJobs.map((job) => job.id)).toEqual(['new-job']);
  });

  it('marks duplicate records inside a backup invalid', () => {
    const first = makeJob({ id: 'one', jobUrl: 'https://example.com/job/1?utm_medium=x' });
    const duplicateId = makeJob({ id: 'one', jobUrl: 'https://example.com/job/2' });
    const duplicateUrl = makeJob({ id: 'two', jobUrl: 'https://www.example.com/job/1/' });

    const plan = createImportPlan(
      {
        schemaVersion: BACKUP_SCHEMA_VERSION,
        exportedAt: new Date().toISOString(),
        jobs: [first, duplicateId, duplicateUrl],
        settings: DEFAULT_SETTINGS,
      },
      [],
    );

    expect(plan.validJobs).toHaveLength(1);
    expect(plan.invalidRecords).toHaveLength(2);
  });
});
