import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, Pencil, Trash2 } from 'lucide-react';
import { JOB_STATUSES, getStatusLabel, type JobStatus } from '../constants/statuses';
import { formatAppliedAge } from '../utils/dates';
import type { Job, SortMode } from '../types/job';
import { SourceBadge } from './SourceBadge';

interface JobCardProps {
  job: Job;
  sortMode: SortMode;
  isSearchActive: boolean;
  onEdit: (job: Job) => void;
  onDelete: (job: Job) => void;
  onStatusChange: (job: Job, status: JobStatus) => void;
}

export function JobCard({
  job,
  sortMode,
  isSearchActive,
  onEdit,
  onDelete,
  onStatusChange,
}: JobCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: job.id,
    data: { type: 'job', status: job.status },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <article
      ref={setNodeRef}
      style={style}
      className={`min-w-0 rounded-lg border border-slate-200 bg-white p-2.5 shadow-sm transition-shadow hover:shadow-md 2xl:p-3 dark:border-slate-700 dark:bg-slate-900 ${
        isDragging ? 'opacity-70 ring-2 ring-emerald-500' : ''
      }`}
    >
      <div className="flex min-w-0 items-start gap-2">
        <button
          type="button"
          className="mt-0.5 inline-flex h-7 w-7 shrink-0 cursor-grab items-center justify-center rounded-md text-slate-400 hover:bg-slate-100 hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 active:cursor-grabbing dark:hover:bg-slate-800 dark:hover:text-slate-100"
          aria-label={`Drag ${job.companyName} ${job.role}`}
          title={
            sortMode === 'manual'
              ? isSearchActive
                ? 'Drag to another stage; same-column reordering is disabled while searching'
                : 'Drag to reorder or move stages'
              : 'Drag to move stages'
          }
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-4 w-4" aria-hidden="true" />
        </button>

        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-slate-950 dark:text-white" title={job.companyName}>
            {job.companyName}
          </h3>
          <p className="mt-0.5 line-clamp-2 text-xs leading-5 text-slate-600 dark:text-slate-300" title={job.role}>
            {job.role}
          </p>
        </div>
        <SourceBadge jobUrl={job.jobUrl} />
      </div>

      <div className="mt-3 flex min-w-0 flex-wrap items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-300">
        {job.resumeName ? (
          <span className="max-w-full truncate rounded-md bg-slate-100 px-2 py-1 dark:bg-slate-800" title={job.resumeName}>
            {job.resumeName}
          </span>
        ) : null}
        <span className="max-w-full truncate rounded-md bg-emerald-50 px-2 py-1 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-100">
          {formatAppliedAge(job.appliedDate)}
        </span>
        {job.salaryRange ? (
          <span className="max-w-full truncate rounded-md bg-amber-50 px-2 py-1 text-amber-900 dark:bg-amber-950 dark:text-amber-100" title={job.salaryRange}>
            {job.salaryRange}
          </span>
        ) : null}
      </div>

      <div className="mt-3 grid gap-2">
        <label className="sr-only" htmlFor={`status-${job.id}`}>
          Change status for {job.companyName} {job.role}
        </label>
        <select
          id={`status-${job.id}`}
          className="field-input h-9 min-w-0 py-1 text-xs"
          value={job.status}
          onChange={(event) => onStatusChange(job, event.target.value as JobStatus)}
          aria-label={`Change status for ${job.companyName} ${job.role}. Current status ${getStatusLabel(job.status)}.`}
        >
          {JOB_STATUSES.map((status) => (
            <option key={status.id} value={status.id}>
              {status.label}
            </option>
          ))}
        </select>
        <div className="flex justify-end gap-2">
          <button
            type="button"
            className="icon-button h-9 w-9"
            onClick={() => onEdit(job)}
            aria-label={`Edit ${job.companyName} ${job.role}`}
            title="Edit"
          >
            <Pencil className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            className="icon-button-danger h-9 w-9"
            onClick={() => onDelete(job)}
            aria-label={`Delete ${job.companyName} ${job.role}`}
            title="Delete"
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </article>
  );
}
