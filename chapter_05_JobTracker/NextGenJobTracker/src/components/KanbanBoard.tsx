import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCorners,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import type { ReactNode } from 'react';
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { JOB_STATUSES, type JobStatus } from '../constants/statuses';
import {
  isKnownStatusId,
  prepareStatusChange,
  sortJobsForColumn,
} from '../services/jobLogic';
import type { Job, SortMode } from '../types/job';
import { JobCard } from './JobCard';

interface KanbanBoardProps {
  jobs: Job[];
  allJobs: Job[];
  query: string;
  sortMode: SortMode;
  onCommit: (changedJobs: Job[], nextJobs: Job[], message: string) => Promise<void>;
  onEdit: (job: Job) => void;
  onDelete: (job: Job) => void;
  onStatusChange: (job: Job, status: JobStatus) => void;
}

function ColumnShell({
  status,
  children,
  totalCount,
  visibleCount,
  isSearchActive,
}: {
  status: (typeof JOB_STATUSES)[number];
  children: ReactNode;
  totalCount: number;
  visibleCount: number;
  isSearchActive: boolean;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status.id });

  return (
    <section
      ref={setNodeRef}
      className={`flex h-full min-h-[560px] w-[320px] shrink-0 flex-col rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950 ${
        isOver ? 'ring-2 ring-emerald-500' : ''
      }`}
      aria-labelledby={`${status.id}-heading`}
    >
      <header className={`border-l-4 ${status.accent} border-b border-b-slate-200 px-3 py-3 dark:border-b-slate-700`}>
        <div className="flex items-center justify-between gap-3">
          <h2 id={`${status.id}-heading`} className="font-semibold text-slate-900 dark:text-slate-100">
            {status.label}
          </h2>
          <span className="rounded-md bg-white px-2 py-1 text-xs font-medium text-slate-700 shadow-sm dark:bg-slate-900 dark:text-slate-200">
            {isSearchActive ? `${visibleCount} / ${totalCount}` : totalCount}
          </span>
        </div>
      </header>
      <div className="flex-1 overflow-y-auto p-3">{children}</div>
    </section>
  );
}

function repositionColumn(jobs: Job[], status: JobStatus, nowIso: string): Job[] {
  return jobs.map((job, index) => ({
    ...job,
    status,
    position: (index + 1) * 1000,
    updatedAt: nowIso,
  }));
}

export function KanbanBoard({
  jobs,
  allJobs,
  query,
  sortMode,
  onCommit,
  onEdit,
  onDelete,
  onStatusChange,
}: KanbanBoardProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const isSearchActive = query.trim().length > 0;

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) {
      return;
    }

    const activeJob = allJobs.find((job) => job.id === active.id);
    if (!activeJob) {
      return;
    }

    const overId = String(over.id);
    const overJob = allJobs.find((job) => job.id === overId);
    const nextStatus = overJob ? overJob.status : isKnownStatusId(overId) ? overId : null;
    if (!nextStatus) {
      return;
    }

    const now = new Date();
    const nowIso = now.toISOString();

    if (activeJob.status === nextStatus) {
      if (sortMode !== 'manual' || isSearchActive || !overJob) {
        return;
      }

      const currentColumn = sortJobsForColumn(
        allJobs.filter((job) => job.status === activeJob.status),
        'manual',
      );
      const oldIndex = currentColumn.findIndex((job) => job.id === activeJob.id);
      const newIndex = currentColumn.findIndex((job) => job.id === overJob.id);
      if (oldIndex < 0 || newIndex < 0 || oldIndex === newIndex) {
        return;
      }

      const reordered = repositionColumn(arrayMove(currentColumn, oldIndex, newIndex), nextStatus, nowIso);
      const nextJobs = allJobs.map((job) => reordered.find((updated) => updated.id === job.id) ?? job);
      await onCommit(reordered, nextJobs, 'Manual order saved.');
      return;
    }

    const movedJob = prepareStatusChange(activeJob, nextStatus, now);
    if (sortMode !== 'manual') {
      const nextJobs = allJobs.map((job) => (job.id === movedJob.id ? movedJob : job));
      await onCommit([movedJob], nextJobs, `Moved to ${JOB_STATUSES.find((status) => status.id === nextStatus)?.label}.`);
      return;
    }

    const sourceColumn = sortJobsForColumn(
      allJobs.filter((job) => job.status === activeJob.status && job.id !== activeJob.id),
      'manual',
    );
    const targetColumn = [
      movedJob,
      ...sortJobsForColumn(
        allJobs.filter((job) => job.status === nextStatus && job.id !== activeJob.id),
        'manual',
      ),
    ];
    const changed = [
      ...repositionColumn(sourceColumn, activeJob.status, nowIso),
      ...repositionColumn(targetColumn, nextStatus, nowIso),
    ];
    const nextJobs = allJobs.map((job) => changed.find((updated) => updated.id === job.id) ?? job);
    await onCommit(changed, nextJobs, `Moved to ${JOB_STATUSES.find((status) => status.id === nextStatus)?.label}.`);
  }

  const totalByStatus = new Map<JobStatus, number>();
  const visibleByStatus = new Map<JobStatus, Job[]>();

  for (const status of JOB_STATUSES) {
    totalByStatus.set(status.id, allJobs.filter((job) => job.status === status.id).length);
    visibleByStatus.set(
      status.id,
      sortJobsForColumn(
        jobs.filter((job) => job.status === status.id),
        sortMode,
      ),
    );
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCorners} onDragEnd={(event) => void handleDragEnd(event)}>
      <div className="overflow-x-auto pb-3">
        <div className="flex min-h-[600px] gap-4">
          {JOB_STATUSES.map((status) => {
            const columnJobs = visibleByStatus.get(status.id) ?? [];
            return (
              <ColumnShell
                key={status.id}
                status={status}
                totalCount={totalByStatus.get(status.id) ?? 0}
                visibleCount={columnJobs.length}
                isSearchActive={isSearchActive}
              >
                <SortableContext items={columnJobs.map((job) => job.id)} strategy={verticalListSortingStrategy}>
                  <div className="space-y-3">
                    {columnJobs.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        sortMode={sortMode}
                        isSearchActive={isSearchActive}
                        onEdit={onEdit}
                        onDelete={onDelete}
                        onStatusChange={onStatusChange}
                      />
                    ))}
                    {columnJobs.length === 0 ? (
                      <p className="rounded-md border border-dashed border-slate-300 px-3 py-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
                        {isSearchActive ? 'No matching jobs' : 'No jobs here'}
                      </p>
                    ) : null}
                  </div>
                </SortableContext>
              </ColumnShell>
            );
          })}
        </div>
      </div>
    </DndContext>
  );
}
