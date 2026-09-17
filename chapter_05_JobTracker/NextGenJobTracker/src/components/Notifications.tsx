import { CheckCircle2, Info, X, XCircle } from 'lucide-react';
import type { ToastMessage } from '../types/job';

interface NotificationsProps {
  messages: ToastMessage[];
  onDismiss: (id: string) => void;
}

export function Notifications({ messages, onDismiss }: NotificationsProps) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="fixed right-4 top-4 z-[60] flex w-[min(92vw,380px)] flex-col gap-3">
      {messages.map((message) => {
        const Icon =
          message.type === 'success' ? CheckCircle2 : message.type === 'error' ? XCircle : Info;
        const tone =
          message.type === 'success'
            ? 'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-100'
            : message.type === 'error'
              ? 'border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-100'
              : 'border-slate-200 bg-white text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100';

        return (
          <div
            key={message.id}
            role={message.type === 'error' ? 'alert' : 'status'}
            className={`flex items-start gap-3 rounded-md border p-3 shadow-soft ${tone}`}
          >
            <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <p className="min-w-0 flex-1 text-sm leading-5">{message.message}</p>
            <button
              type="button"
              className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md hover:bg-black/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500"
              onClick={() => onDismiss(message.id)}
              aria-label="Dismiss notification"
              title="Dismiss notification"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
