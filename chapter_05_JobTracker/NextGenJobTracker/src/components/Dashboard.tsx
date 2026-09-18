import {
  BellRing,
  Bookmark,
  BriefcaseBusiness,
  CircleX,
  Handshake,
  MessagesSquare,
  Send,
  type LucideIcon,
} from 'lucide-react';
import { useMemo } from 'react';
import type { JobStatus } from '../constants/statuses';
import { calculateDashboardMetrics, type StatusMetric } from '../services/dashboardMetrics';
import type { Job } from '../types/job';

interface DashboardProps {
  jobs: Job[];
}

interface StatusVisual {
  label: string;
  icon: LucideIcon;
  color: string;
  bar: string;
  card: string;
  iconSurface: string;
}

const STATUS_VISUALS: Record<JobStatus, StatusVisual> = {
  wishlist: {
    label: 'Wishlisted',
    icon: Bookmark,
    color: '#64748b',
    bar: 'bg-slate-500',
    card: 'border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900',
    iconSurface: 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-100',
  },
  applied: {
    label: 'Applied',
    icon: Send,
    color: '#0ea5e9',
    bar: 'bg-sky-500',
    card: 'border-sky-200 bg-sky-50 dark:border-sky-900 dark:bg-sky-950/45',
    iconSurface: 'bg-sky-100 text-sky-700 dark:bg-sky-900 dark:text-sky-200',
  },
  'follow-up': {
    label: 'Follow-up',
    icon: BellRing,
    color: '#f59e0b',
    bar: 'bg-amber-500',
    card: 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/45',
    iconSurface: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-200',
  },
  interview: {
    label: 'Interview',
    icon: MessagesSquare,
    color: '#8b5cf6',
    bar: 'bg-violet-500',
    card: 'border-violet-200 bg-violet-50 dark:border-violet-900 dark:bg-violet-950/45',
    iconSurface: 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-200',
  },
  offer: {
    label: 'Offer',
    icon: Handshake,
    color: '#10b981',
    bar: 'bg-emerald-500',
    card: 'border-emerald-200 bg-emerald-50 dark:border-emerald-900 dark:bg-emerald-950/45',
    iconSurface: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
  },
  rejected: {
    label: 'Rejected',
    icon: CircleX,
    color: '#f43f5e',
    bar: 'bg-rose-500',
    card: 'border-rose-200 bg-rose-50 dark:border-rose-900 dark:bg-rose-950/45',
    iconSurface: 'bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-200',
  },
};

export function Dashboard({ jobs }: DashboardProps) {
  const metrics = useMemo(() => calculateDashboardMetrics(jobs), [jobs]);

  return (
    <div className="space-y-5" data-testid="dashboard">
      <section aria-labelledby="metrics-heading">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 id="metrics-heading" className="text-lg font-semibold text-slate-950 dark:text-slate-50">
            Application overview
          </h2>
          <span className="text-sm text-slate-500 dark:text-slate-400">Current status</span>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            label="Total number of jobs"
            value={metrics.total}
            icon={BriefcaseBusiness}
            className="border-indigo-200 bg-indigo-50 dark:border-indigo-900 dark:bg-indigo-950/45"
            iconClassName="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200"
          />
          {metrics.statuses.map((metric) => {
            const visual = STATUS_VISUALS[metric.status];
            return (
              <MetricCard
                key={metric.status}
                label={visual.label}
                value={metric.count}
                icon={visual.icon}
                className={visual.card}
                iconClassName={visual.iconSurface}
              />
            );
          })}
        </div>
      </section>

      <section className="grid min-w-0 gap-4 lg:grid-cols-[minmax(280px,0.8fr)_minmax(0,1.2fr)]" aria-label="Application status distribution">
        <StatusDonut metrics={metrics.statuses} total={metrics.total} />
        <StatusBars metrics={metrics.statuses} />
      </section>

      <section className="grid min-w-0 gap-4 lg:grid-cols-2" aria-label="Application outcomes">
        <OutcomeColumn status="offer" jobs={metrics.offers} />
        <OutcomeColumn status="rejected" jobs={metrics.rejected} />
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon: Icon,
  className,
  iconClassName,
}: {
  label: string;
  value: number;
  icon: LucideIcon;
  className: string;
  iconClassName: string;
}) {
  return (
    <article
      className={`flex min-h-28 items-center justify-between gap-4 rounded-lg border p-4 shadow-sm ${className}`}
      aria-label={`${label}: ${value}`}
    >
      <div className="min-w-0">
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300">{label}</p>
        <p className="mt-1 text-3xl font-semibold text-slate-950 dark:text-white">{value}</p>
      </div>
      <span className={`inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${iconClassName}`} aria-hidden="true">
        <Icon className="h-5 w-5" />
      </span>
    </article>
  );
}

function StatusDonut({ metrics, total }: { metrics: StatusMetric[]; total: number }) {
  let offset = 0;
  const description = total === 0
    ? 'No jobs have been saved.'
    : metrics.map((metric) => `${STATUS_VISUALS[metric.status].label}: ${metric.count}`).join(', ');

  return (
    <figure className="flex min-h-[320px] flex-col rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <figcaption className="text-base font-semibold text-slate-950 dark:text-slate-50">Status distribution</figcaption>
      <div className="flex flex-1 items-center justify-center py-3">
        <svg className="h-56 w-56 max-w-full" viewBox="0 0 160 160" role="img" aria-labelledby="status-chart-title status-chart-description">
          <title id="status-chart-title">Job status distribution</title>
          <desc id="status-chart-description">{description}</desc>
          <circle cx="80" cy="80" r="56" fill="none" stroke="currentColor" strokeWidth="18" className="text-slate-200 dark:text-slate-700" />
          {total > 0
            ? metrics.map((metric) => {
                const currentOffset = offset;
                offset += metric.share;
                return metric.count > 0 ? (
                  <circle
                    key={metric.status}
                    cx="80"
                    cy="80"
                    r="56"
                    fill="none"
                    pathLength="100"
                    stroke={STATUS_VISUALS[metric.status].color}
                    strokeDasharray={`${metric.share} ${100 - metric.share}`}
                    strokeDashoffset={-currentOffset}
                    strokeWidth="18"
                    transform="rotate(-90 80 80)"
                  />
                ) : null;
              })
            : null}
          <text x="80" y="75" textAnchor="middle" className="fill-slate-500 text-[9px] font-medium uppercase dark:fill-slate-400">
            Total jobs
          </text>
          <text x="80" y="96" textAnchor="middle" className="fill-slate-950 text-[22px] font-semibold dark:fill-white">
            {total}
          </text>
        </svg>
      </div>
      {total === 0 ? <p className="text-center text-sm text-slate-500 dark:text-slate-400">No application data yet</p> : null}
    </figure>
  );
}

function StatusBars({ metrics }: { metrics: StatusMetric[] }) {
  return (
    <section className="min-h-[320px] rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900" aria-labelledby="status-breakdown-heading">
      <h3 id="status-breakdown-heading" className="text-base font-semibold text-slate-950 dark:text-slate-50">
        Status breakdown
      </h3>
      <div className="mt-5 space-y-4">
        {metrics.map((metric) => {
          const visual = STATUS_VISUALS[metric.status];
          const width = metric.count > 0 ? Math.max(metric.share, 1) : 0;
          return (
            <div key={metric.status}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <div className="flex min-w-0 items-center gap-2">
                  <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${visual.bar}`} aria-hidden="true" />
                  <span className="truncate font-medium text-slate-700 dark:text-slate-200">{visual.label}</span>
                </div>
                <span className="shrink-0 tabular-nums text-slate-500 dark:text-slate-400">
                  {metric.count} · {metric.percentage}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800" aria-hidden="true">
                <div className={`h-full rounded-full ${visual.bar}`} style={{ width: `${width}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function OutcomeColumn({ status, jobs }: { status: 'offer' | 'rejected'; jobs: Job[] }) {
  const isOffer = status === 'offer';
  const title = isOffer ? 'Offer' : 'Rejected';
  const Icon = isOffer ? Handshake : CircleX;
  const headingId = `${status}-outcomes-heading`;

  return (
    <section
      className={`overflow-hidden rounded-lg border shadow-sm ${
        isOffer
          ? 'border-emerald-200 bg-emerald-50/70 dark:border-emerald-900 dark:bg-emerald-950/35'
          : 'border-rose-200 bg-rose-50/70 dark:border-rose-900 dark:bg-rose-950/35'
      }`}
      aria-labelledby={headingId}
    >
      <header className={`flex items-center justify-between gap-3 border-b px-4 py-3 ${isOffer ? 'border-emerald-200 dark:border-emerald-900' : 'border-rose-200 dark:border-rose-900'}`}>
        <div className="flex items-center gap-2.5">
          <span className={`inline-flex h-9 w-9 items-center justify-center rounded-lg ${isOffer ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200' : 'bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-200'}`} aria-hidden="true">
            <Icon className="h-4 w-4" />
          </span>
          <h3 id={headingId} className={`font-semibold ${isOffer ? 'text-emerald-950 dark:text-emerald-100' : 'text-rose-950 dark:text-rose-100'}`}>
            {title}
          </h3>
        </div>
        <span className={`rounded-md px-2.5 py-1 text-xs font-semibold tabular-nums ${isOffer ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-100' : 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-100'}`}>
          {jobs.length}
        </span>
      </header>

      {jobs.length > 0 ? (
        <ul className={`max-h-80 overflow-y-auto divide-y ${isOffer ? 'divide-emerald-200 dark:divide-emerald-900' : 'divide-rose-200 dark:divide-rose-900'}`}>
          {jobs.map((job) => (
            <li key={job.id} className="px-4 py-3">
              <p className="break-words text-sm font-semibold text-slate-950 dark:text-white">{job.companyName}</p>
              <p className="mt-0.5 break-words text-sm text-slate-600 dark:text-slate-300">{job.role}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className={`px-4 py-8 text-center text-sm ${isOffer ? 'text-emerald-800 dark:text-emerald-200' : 'text-rose-800 dark:text-rose-200'}`}>
          {isOffer ? 'No offers yet' : 'No rejected applications'}
        </p>
      )}
    </section>
  );
}
