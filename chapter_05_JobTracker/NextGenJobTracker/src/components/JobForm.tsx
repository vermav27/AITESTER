import { ChevronDown, Save } from 'lucide-react';
import type { FormEvent } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { JOB_STATUSES } from '../constants/statuses';
import {
  createEmptyDraft,
  findDuplicateByUrl,
  hasFieldErrors,
  jobToDraft,
  validateJobDraft,
} from '../services/jobLogic';
import type { FieldErrors, Job, JobDraft } from '../types/job';
import { todayLocalDate } from '../utils/dates';
import { ConfirmDialog } from './ConfirmDialog';
import { Modal } from './Modal';

interface JobFormProps {
  job: Job | null;
  jobs: Job[];
  resumeNames: string[];
  onSave: (draft: JobDraft) => Promise<void>;
  onClose: () => void;
}

export function JobForm({ job, jobs, resumeNames, onSave, onClose }: JobFormProps) {
  const [draft, setDraft] = useState<JobDraft>(() => (job ? jobToDraft(job) : createEmptyDraft()));
  const [initialSnapshot, setInitialSnapshot] = useState('');
  const [errors, setErrors] = useState<FieldErrors>({});
  const [saving, setSaving] = useState(false);
  const [duplicateJob, setDuplicateJob] = useState<Job | null>(null);
  const [duplicateAcknowledged, setDuplicateAcknowledged] = useState(false);
  const [confirmDiscard, setConfirmDiscard] = useState(false);

  useEffect(() => {
    const nextDraft = job ? jobToDraft(job) : createEmptyDraft();
    setDraft(nextDraft);
    setInitialSnapshot(JSON.stringify(nextDraft));
    setErrors({});
    setDuplicateJob(null);
    setDuplicateAcknowledged(false);
  }, [job]);

  const isDirty = useMemo(() => JSON.stringify(draft) !== initialSnapshot, [draft, initialSnapshot]);

  function updateField<K extends keyof JobDraft>(key: K, value: JobDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined }));
    if (key === 'jobUrl') {
      setDuplicateJob(null);
      setDuplicateAcknowledged(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (saving) {
      return;
    }

    const validation = validateJobDraft(draft);
    setErrors(validation);
    if (hasFieldErrors(validation)) {
      return;
    }

    const duplicate = findDuplicateByUrl(draft.jobUrl, jobs, job?.id);
    if (duplicate && !duplicateAcknowledged) {
      setDuplicateJob(duplicate);
      return;
    }

    setSaving(true);
    try {
      await onSave(draft);
    } finally {
      setSaving(false);
    }
  }

  function requestClose() {
    if (isDirty && !saving) {
      setConfirmDiscard(true);
      return;
    }
    onClose();
  }

  return (
    <>
      <Modal title={job ? 'Edit job' : 'Add job'} onClose={requestClose} size="lg">
        <form className="space-y-5" onSubmit={(event) => void handleSubmit(event)}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="field-label">
              Company name
              <input
                className="field-input"
                value={draft.companyName}
                onChange={(event) => updateField('companyName', event.target.value)}
                aria-invalid={Boolean(errors.companyName)}
                aria-describedby={errors.companyName ? 'company-error' : undefined}
                required
              />
              {errors.companyName ? <span id="company-error" className="field-error">{errors.companyName}</span> : null}
            </label>

            <label className="field-label">
              Role
              <input
                className="field-input"
                value={draft.role}
                onChange={(event) => updateField('role', event.target.value)}
                aria-invalid={Boolean(errors.role)}
                aria-describedby={errors.role ? 'role-error' : undefined}
                required
              />
              {errors.role ? <span id="role-error" className="field-error">{errors.role}</span> : null}
            </label>

            <label className="field-label">
              Status
              <div className="select-control">
                <select
                  className="field-input"
                  value={draft.status}
                  onChange={(event) => updateField('status', event.target.value as JobDraft['status'])}
                >
                  {JOB_STATUSES.map((status) => (
                    <option key={status.id} value={status.id}>
                      {status.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="select-chevron" aria-hidden="true" />
              </div>
            </label>

            <label className="field-label">
              Job URL
              <input
                className="field-input"
                value={draft.jobUrl}
                onChange={(event) => updateField('jobUrl', event.target.value)}
                placeholder="https://..."
                aria-invalid={Boolean(errors.jobUrl)}
                aria-describedby={errors.jobUrl ? 'url-error' : undefined}
              />
              {errors.jobUrl ? <span id="url-error" className="field-error">{errors.jobUrl}</span> : null}
            </label>
          </div>

          <details className="rounded-md border border-slate-200 p-4 dark:border-slate-700" open>
            <summary className="cursor-pointer text-sm font-semibold text-slate-800 dark:text-slate-100">
              Additional details
            </summary>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className="field-label">
                Resume used
                <input
                  className="field-input"
                  value={draft.resumeName}
                  list="resume-options"
                  onChange={(event) => updateField('resumeName', event.target.value)}
                />
                <datalist id="resume-options">
                  {resumeNames.map((resume) => (
                    <option key={resume} value={resume} />
                  ))}
                </datalist>
              </label>

              <label className="field-label">
                Applied date
                <input
                  className="field-input"
                  type="date"
                  max={todayLocalDate()}
                  value={draft.appliedDate}
                  onChange={(event) => updateField('appliedDate', event.target.value)}
                  aria-invalid={Boolean(errors.appliedDate)}
                  aria-describedby={errors.appliedDate ? 'applied-date-error' : undefined}
                />
                {errors.appliedDate ? (
                  <span id="applied-date-error" className="field-error">
                    {errors.appliedDate}
                  </span>
                ) : null}
              </label>

              <label className="field-label">
                Salary range
                <input
                  className="field-input"
                  value={draft.salaryRange}
                  onChange={(event) => updateField('salaryRange', event.target.value)}
                />
              </label>

              <label className="field-label sm:col-span-2">
                Notes
                <textarea
                  className="field-input min-h-28"
                  value={draft.notes}
                  onChange={(event) => updateField('notes', event.target.value)}
                />
              </label>
            </div>
          </details>

          {duplicateJob ? (
            <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100">
              <p>
                This URL looks like an existing job for {duplicateJob.companyName} - {duplicateJob.role}.
              </p>
              <label className="mt-3 flex items-start gap-2">
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={duplicateAcknowledged}
                  onChange={(event) => setDuplicateAcknowledged(event.target.checked)}
                />
                <span>Save anyway because this is a deliberate duplicate.</span>
              </label>
            </div>
          ) : null}

          <div className="flex flex-wrap justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={requestClose} disabled={saving}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={saving || Boolean(duplicateJob && !duplicateAcknowledged)}
            >
              <Save className="h-4 w-4" aria-hidden="true" />
              {saving ? 'Saving...' : duplicateJob ? 'Save anyway' : 'Save job'}
            </button>
          </div>
        </form>
      </Modal>

      {confirmDiscard ? (
        <ConfirmDialog
          title="Discard changes?"
          message="This job has unsaved changes. Discard them and close the form?"
          confirmLabel="Discard changes"
          destructive
          onCancel={() => setConfirmDiscard(false)}
          onConfirm={() => {
            setConfirmDiscard(false);
            onClose();
          }}
        />
      ) : null}
    </>
  );
}
