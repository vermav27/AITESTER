import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel?: string;
  destructive?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel,
  cancelLabel = 'Cancel',
  destructive = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Modal title={title} onClose={onCancel} size="sm">
      <div className="flex gap-3">
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-md ${
            destructive
              ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-200'
              : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-200'
          }`}
        >
          <AlertTriangle className="h-5 w-5" aria-hidden="true" />
        </div>
        <p className="text-sm leading-6 text-slate-700 dark:text-slate-200">{message}</p>
      </div>
      <div className="mt-5 flex justify-end gap-3">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          {cancelLabel}
        </button>
        <button
          type="button"
          className={destructive ? 'btn-danger' : 'btn-primary'}
          onClick={() => void onConfirm()}
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
