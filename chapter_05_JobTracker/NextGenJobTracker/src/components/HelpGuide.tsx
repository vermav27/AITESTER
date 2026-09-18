import { BookOpen, Database, Download, ExternalLink, ListChecks, MoveRight, Plus } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Modal } from './Modal';
import { UserGuideViewer } from './UserGuideViewer';

interface HelpGuideProps {
  onClose: () => void;
}

const guideItems = [
  {
    icon: Plus,
    title: 'Add a job',
    copy: 'Enter the company, role and optional job link.',
  },
  {
    icon: MoveRight,
    title: 'Move it through stages',
    copy: 'Drag a card or use its status menu.',
  },
  {
    icon: ExternalLink,
    title: 'Open the original listing',
    copy: 'Select the platform icon.',
  },
  {
    icon: ListChecks,
    title: 'Find and organize jobs',
    copy: 'Use search and sorting.',
  },
  {
    icon: Download,
    title: 'Back up your data',
    copy: 'Export JSON regularly and use Import to restore it.',
  },
];

const userGuideUrl = new URL(
  '../../Architecture/NextGenJobTracker_User_Guide.pdf',
  import.meta.url,
).href;

export function HelpGuide({ onClose }: HelpGuideProps) {
  const [view, setView] = useState<'help' | 'viewer'>('help');
  const launcherRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    launcherRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  }, []);

  const closeHelp = () => {
    onClose();
    window.requestAnimationFrame(() => launcherRef.current?.focus());
  };

  if (view === 'viewer') {
    return <UserGuideViewer pdfUrl={userGuideUrl} onBack={() => setView('help')} />;
  }

  return (
    <Modal
      title="How to use this tracker"
      onClose={closeHelp}
      size="lg"
      headerAction={
        <button
          type="button"
          className="btn-secondary h-9 px-3"
          onClick={() => setView('viewer')}
        >
          <BookOpen className="h-4 w-4" aria-hidden="true" />
          View User Guide
        </button>
      }
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {guideItems.map((item) => (
          <div
            key={item.title}
            className="rounded-md border border-slate-200 p-4 dark:border-slate-700"
          >
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-md bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
              <item.icon className="h-4 w-4" aria-hidden="true" />
            </div>
            <h3 className="font-semibold">{item.title}</h3>
            <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{item.copy}</p>
          </div>
        ))}
      </div>

      <section className="mt-5 rounded-md border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-emerald-600 dark:text-emerald-300" aria-hidden="true" />
          <h3 className="font-semibold">Your data stays in this browser</h3>
        </div>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
          <li>No login or cloud synchronization exists.</li>
          <li>Browser data can be cleared.</li>
          <li>Different browsers and domains have separate data.</li>
          <li>JSON export is the backup mechanism.</li>
        </ul>
      </section>

      <div className="mt-5 flex justify-end">
        <button type="button" className="btn-primary" onClick={closeHelp}>
          Close
        </button>
      </div>
    </Modal>
  );
}
