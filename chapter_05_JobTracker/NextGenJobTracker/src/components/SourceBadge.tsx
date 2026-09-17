import { ExternalLink } from 'lucide-react';
import { detectPlatform } from '../platforms/registry';

interface SourceBadgeProps {
  jobUrl?: string;
}

export function SourceBadge({ jobUrl }: SourceBadgeProps) {
  const source = detectPlatform(jobUrl);
  if (!jobUrl || !source) {
    return null;
  }

  return (
    <a
      href={jobUrl}
      target="_blank"
      rel="noopener noreferrer"
      title={source.externalLinkLabel}
      aria-label={source.externalLinkLabel}
      className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 shadow-sm hover:border-emerald-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
    >
      {source.icon.type === 'simple-icons' ? (
        <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true">
          <path d={source.icon.icon.path} fill={`#${source.icon.icon.hex}`} />
        </svg>
      ) : source.icon.type === 'initials' ? (
        <span
          className="flex h-[18px] min-w-[18px] items-center justify-center rounded-sm px-0.5 text-[10px] font-bold leading-none text-white"
          style={{ backgroundColor: source.icon.color }}
          aria-hidden="true"
        >
          {source.icon.initials}
        </span>
      ) : (
        <ExternalLink className="h-[18px] w-[18px]" aria-hidden="true" />
      )}
    </a>
  );
}
