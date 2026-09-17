import {
  Download,
  HelpCircle,
  Plus,
  Search,
  Trash2,
  Upload,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { JOB_STATUSES, type JobStatus } from './constants/statuses';
import { replaceDatabaseContents } from './repositories/backupRepository';
import { DEFAULT_SETTINGS } from './repositories/contracts';
import { IndexedDbJobRepository, IndexedDbSettingsRepository } from './repositories/indexedDb';
import {
  buildBackup,
  createImportPlan,
  getBackupFilename,
  parseBackupJson,
  type ImportPlan,
} from './services/importExport';
import {
  buildJobFromDraft,
  getNextPosition,
  prepareStatusChange,
  searchJobs,
  sortJobsForColumn,
} from './services/jobLogic';
import type { AppSettings, Job, JobDraft, SortMode, ThemePreference, ToastMessage } from './types/job';
import { ConfirmDialog } from './components/ConfirmDialog';
import { HelpGuide } from './components/HelpGuide';
import { JobForm } from './components/JobForm';
import { KanbanBoard } from './components/KanbanBoard';
import { Modal } from './components/Modal';
import { Notifications } from './components/Notifications';

const jobRepository = new IndexedDbJobRepository();
const settingsRepository = new IndexedDbSettingsRepository();

function useResolvedTheme(theme: ThemePreference) {
  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const applyTheme = () => {
      const shouldUseDark = theme === 'dark' || (theme === 'system' && media.matches);
      document.documentElement.classList.toggle('dark', shouldUseDark);
      document.documentElement.style.colorScheme = shouldUseDark ? 'dark' : 'light';
    };

    applyTheme();
    media.addEventListener('change', applyTheme);
    return () => media.removeEventListener('change', applyTheme);
  }, [theme]);
}

function createToast(type: ToastMessage['type'], message: string, persistent = false): ToastMessage {
  return {
    id: crypto.randomUUID(),
    type,
    message,
    persistent,
  };
}

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);
  const [formJob, setFormJob] = useState<Job | null | 'new'>(null);
  const [deleteJob, setDeleteJob] = useState<Job | null>(null);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ToastMessage[]>([]);
  const [showHelp, setShowHelp] = useState(false);
  const [importPlan, setImportPlan] = useState<ImportPlan | null>(null);
  const [replaceConfirmed, setReplaceConfirmed] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useResolvedTheme(settings.theme);

  const filteredJobs = useMemo(() => searchJobs(jobs, query), [jobs, query]);
  const resumeNames = useMemo(
    () =>
      Array.from(new Set(jobs.map((job) => job.resumeName).filter((resume): resume is string => Boolean(resume)))).sort(
        (a, b) => a.localeCompare(b),
      ),
    [jobs],
  );

  function pushToast(type: ToastMessage['type'], message: string, persistent = false) {
    const toast = createToast(type, message, persistent);
    setMessages((current) => [toast, ...current].slice(0, 5));
    if (!persistent) {
      window.setTimeout(() => {
        setMessages((current) => current.filter((item) => item.id !== toast.id));
      }, 4500);
    }
  }

  useEffect(() => {
    async function load() {
      try {
        const [savedJobs, savedSettings] = await Promise.all([
          jobRepository.list(),
          settingsRepository.get(),
        ]);
        setJobs(savedJobs);
        setSettings(savedSettings);
        if (savedJobs.length === 0 && !savedSettings.hasSeenGuide) {
          setShowHelp(true);
        }
      } catch (error) {
        pushToast('error', `Could not open browser storage: ${getErrorMessage(error)}`, true);
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  async function updateSettings(nextSettings: AppSettings, successMessage?: string) {
    try {
      await settingsRepository.save(nextSettings);
      setSettings(nextSettings);
      if (successMessage) {
        pushToast('success', successMessage);
      }
    } catch (error) {
      pushToast('error', `Settings were not saved: ${getErrorMessage(error)}`, true);
    }
  }

  async function handleHelpClose() {
    setShowHelp(false);
    if (!settings.hasSeenGuide) {
      await updateSettings({ ...settings, hasSeenGuide: true });
    }
  }

  async function handleThemeChange(theme: ThemePreference) {
    await updateSettings({ ...settings, theme }, 'Theme preference saved.');
  }

  async function handleSortChange(sortMode: SortMode) {
    await updateSettings({ ...settings, sortMode }, 'Sort preference saved.');
  }

  async function handleSaveDraft(draft: JobDraft) {
    const existing = formJob && formJob !== 'new' ? formJob : null;
    const job = buildJobFromDraft(draft, existing, getNextPosition(jobs));
    try {
      await jobRepository.save(job);
      setJobs((current) => {
        if (existing) {
          return current.map((item) => (item.id === job.id ? job : item));
        }
        return [...current, job];
      });
      setFormJob(null);
      pushToast('success', existing ? 'Job updated.' : 'Job added.');
    } catch (error) {
      pushToast('error', `Job was not saved: ${getErrorMessage(error)}`, true);
      throw error;
    }
  }

  async function commitJobs(changedJobs: Job[], nextJobs: Job[], message: string) {
    try {
      await jobRepository.saveMany(changedJobs);
      setJobs(nextJobs);
      pushToast('success', message);
    } catch (error) {
      pushToast('error', `Change was not saved: ${getErrorMessage(error)}`, true);
    }
  }

  async function handleStatusChange(job: Job, status: JobStatus) {
    if (job.status === status) {
      return;
    }

    const updated = prepareStatusChange(job, status);
    if (settings.sortMode === 'manual') {
      const nowIso = updated.updatedAt;
      const sourceColumn = sortJobsForColumn(
        jobs.filter((item) => item.status === job.status && item.id !== job.id),
        'manual',
      ).map((item, index) => ({
        ...item,
        position: (index + 1) * 1000,
        updatedAt: nowIso,
      }));
      const targetColumn = [
        updated,
        ...sortJobsForColumn(
          jobs.filter((item) => item.status === status && item.id !== job.id),
          'manual',
        ),
      ].map((item, index) => ({
        ...item,
        status,
        position: (index + 1) * 1000,
        updatedAt: nowIso,
      }));
      const changedJobs = [...sourceColumn, ...targetColumn];
      await commitJobs(
        changedJobs,
        jobs.map((item) => changedJobs.find((candidate) => candidate.id === item.id) ?? item),
        `Moved to ${JOB_STATUSES.find((candidate) => candidate.id === status)?.label}.`,
      );
      return;
    }

    await commitJobs(
      [updated],
      jobs.map((item) => (item.id === job.id ? updated : item)),
      `Moved to ${JOB_STATUSES.find((candidate) => candidate.id === status)?.label}.`,
    );
  }

  async function handleDeleteConfirmed() {
    if (!deleteJob) {
      return;
    }

    try {
      await jobRepository.delete(deleteJob.id);
      setJobs((current) => current.filter((job) => job.id !== deleteJob.id));
      pushToast('success', 'Job deleted.');
      setDeleteJob(null);
    } catch (error) {
      pushToast('error', `Job was not deleted: ${getErrorMessage(error)}`, true);
    }
  }

  function handleExport() {
    const backup = buildBackup(jobs, settings);
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = getBackupFilename();
    anchor.click();
    URL.revokeObjectURL(url);
    pushToast('success', 'Backup JSON exported.');
  }

  async function handleImportFile(file: File) {
    setImportError(null);
    setReplaceConfirmed(false);
    try {
      const text = await file.text();
      const parsed = parseBackupJson(text);
      setImportPlan(createImportPlan(parsed, jobs));
    } catch (error) {
      setImportError(getErrorMessage(error));
      setImportPlan(null);
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }

  async function handleMergeImport() {
    if (!importPlan) {
      return;
    }

    try {
      await jobRepository.mergeNew(importPlan.importableJobs);
      setJobs((current) => [...current, ...importPlan.importableJobs]);
      pushToast(
        'success',
        `Imported ${importPlan.importableJobs.length}; skipped ${importPlan.conflicts.length + importPlan.invalidRecords.length}.`,
      );
      setImportPlan(null);
    } catch (error) {
      pushToast('error', `Import failed and existing data was preserved: ${getErrorMessage(error)}`, true);
    }
  }

  async function handleReplaceImport() {
    if (!importPlan || importPlan.invalidRecords.length > 0 || !replaceConfirmed) {
      return;
    }

    try {
      await replaceDatabaseContents(importPlan.validJobs, importPlan.settings);
      setJobs(importPlan.validJobs);
      setSettings(importPlan.settings);
      pushToast('success', `Replaced tracker data with ${importPlan.validJobs.length} imported jobs.`);
      setImportPlan(null);
      setReplaceConfirmed(false);
    } catch (error) {
      pushToast('error', `Replace failed and existing data was preserved: ${getErrorMessage(error)}`, true);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <p className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm dark:border-slate-700 dark:bg-slate-900">
          Loading local tracker...
        </p>
      </main>
    );
  }

  const isEmpty = jobs.length === 0;

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950 dark:bg-slate-950 dark:text-slate-50">
      <Notifications messages={messages} onDismiss={(id) => setMessages((current) => current.filter((message) => message.id !== id))} />

      <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-4 px-4 py-4 lg:px-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold tracking-normal">NextGen Job Tracker</h1>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                Local-first applications board stored in this browser.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                className="icon-button"
                onClick={() => setShowHelp(true)}
                aria-label="How to use tracker?"
                title="How to use tracker?"
              >
                <HelpCircle className="h-4 w-4" aria-hidden="true" />
              </button>
              <button type="button" className="btn-secondary" onClick={handleExport} disabled={jobs.length === 0}>
                <Download className="h-4 w-4" aria-hidden="true" />
                Export
              </button>
              <button type="button" className="btn-secondary" onClick={() => fileInputRef.current?.click()}>
                <Upload className="h-4 w-4" aria-hidden="true" />
                Import
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="application/json,.json"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void handleImportFile(file);
                  }
                }}
              />
              <button type="button" className="btn-primary" onClick={() => setFormJob('new')}>
                <Plus className="h-4 w-4" aria-hidden="true" />
                Add job
              </button>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-[minmax(260px,1fr)_auto_auto]">
            <label className="relative block">
              <span className="sr-only">Search company and role</span>
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                className="field-input h-10 pl-9 pr-10"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search company or role"
              />
              {query ? (
                <button
                  type="button"
                  className="absolute right-2 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 dark:hover:bg-slate-800"
                  onClick={() => setQuery('')}
                  aria-label="Clear search"
                  title="Clear search"
                >
                  <X className="h-4 w-4" aria-hidden="true" />
                </button>
              ) : null}
            </label>

            <label className="field-label compact">
              Sort
              <select className="field-input h-10" value={settings.sortMode} onChange={(event) => void handleSortChange(event.target.value as SortMode)}>
                <option value="manual">Manual</option>
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
              </select>
            </label>

            <label className="field-label compact">
              Theme
              <select className="field-input h-10" value={settings.theme} onChange={(event) => void handleThemeChange(event.target.value as ThemePreference)}>
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-[1500px] px-4 py-5 lg:px-6">
        {isEmpty ? (
          <div className="mx-auto mt-10 max-w-2xl rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <h2 className="text-xl font-semibold">Start tracking your applications</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Add roles from job boards, company career pages or recruiter links. Your data remains in the current browser profile and should be backed up with JSON export.
            </p>
            <div className="mt-5 flex flex-wrap justify-center gap-3">
              <button type="button" className="btn-primary" onClick={() => setFormJob('new')}>
                <Plus className="h-4 w-4" aria-hidden="true" />
                Add your first job
              </button>
              <button type="button" className="btn-secondary" onClick={() => setShowHelp(true)}>
                <HelpCircle className="h-4 w-4" aria-hidden="true" />
                How to use tracker?
              </button>
            </div>
          </div>
        ) : (
          <>
            {query.trim() && filteredJobs.length === 0 ? (
              <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100">
                No matching jobs.
              </div>
            ) : null}
            <KanbanBoard
              jobs={filteredJobs}
              allJobs={jobs}
              query={query}
              sortMode={settings.sortMode}
              onCommit={commitJobs}
              onEdit={(job) => setFormJob(job)}
              onDelete={(job) => setDeleteJob(job)}
              onStatusChange={(job, status) => void handleStatusChange(job, status)}
            />
          </>
        )}
      </section>

      {formJob ? (
        <JobForm
          job={formJob === 'new' ? null : formJob}
          jobs={jobs}
          resumeNames={resumeNames}
          onSave={handleSaveDraft}
          onClose={() => setFormJob(null)}
        />
      ) : null}

      {deleteJob ? (
        <ConfirmDialog
          title="Delete job?"
          message={`Delete ${deleteJob.companyName} - ${deleteJob.role}? This cannot be undone.`}
          confirmLabel="Delete job"
          destructive
          onCancel={() => setDeleteJob(null)}
          onConfirm={() => void handleDeleteConfirmed()}
        />
      ) : null}

      {showHelp ? <HelpGuide onClose={() => void handleHelpClose()} /> : null}

      {importError ? (
        <Modal title="Import failed" onClose={() => setImportError(null)} size="sm">
          <p className="text-sm leading-6 text-slate-700 dark:text-slate-200">{importError}</p>
          <div className="mt-5 flex justify-end">
            <button type="button" className="btn-primary" onClick={() => setImportError(null)}>
              Close
            </button>
          </div>
        </Modal>
      ) : null}

      {importPlan ? (
        <Modal title="Review import" onClose={() => setImportPlan(null)} size="lg">
          <div className="grid gap-3 sm:grid-cols-3">
            <ImportMetric label="Valid" value={importPlan.validJobs.length} />
            <ImportMetric label="Invalid" value={importPlan.invalidRecords.length} />
            <ImportMetric label="Conflicting" value={importPlan.conflicts.length} />
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">
            Merge keeps existing jobs and imports only valid non-conflicting records. Replace clears the tracker and restores the backup after full validation.
          </p>

          {importPlan.invalidRecords.length > 0 ? (
            <div className="mt-4 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-950 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-100">
              <p className="font-semibold">Invalid records</p>
              <ul className="mt-2 space-y-1">
                {importPlan.invalidRecords.slice(0, 5).map((record) => (
                  <li key={`${record.index}-${record.reason}`}>
                    #{record.index + 1}: {record.reason}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {importPlan.conflicts.length > 0 ? (
            <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100">
              <p className="font-semibold">Conflicts skipped during merge</p>
              <ul className="mt-2 space-y-1">
                {importPlan.conflicts.slice(0, 5).map((conflict) => (
                  <li key={`${conflict.index}-${conflict.incoming.id}`}>
                    #{conflict.index + 1}: {conflict.incoming.companyName} conflicts with {conflict.existing.companyName} by {conflict.reason}.
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <label className="mt-4 flex items-start gap-2 text-sm text-slate-700 dark:text-slate-200">
            <input
              type="checkbox"
              className="mt-1"
              checked={replaceConfirmed}
              onChange={(event) => setReplaceConfirmed(event.target.checked)}
              disabled={importPlan.invalidRecords.length > 0}
            />
            <span>Allow Replace to clear current jobs and restore the validated backup.</span>
          </label>

          <div className="mt-5 flex flex-wrap justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={() => setImportPlan(null)}>
              Cancel
            </button>
            <button type="button" className="btn-primary" onClick={() => void handleMergeImport()}>
              Merge
            </button>
            <button
              type="button"
              className="btn-danger"
              disabled={importPlan.invalidRecords.length > 0 || !replaceConfirmed}
              onClick={() => void handleReplaceImport()}
            >
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Replace
            </button>
          </div>
        </Modal>
      ) : null}
    </main>
  );
}

function ImportMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-slate-200 p-3 dark:border-slate-700">
      <p className="text-xs uppercase tracking-normal text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unknown error';
}
