import type { JobStatus } from '../constants/statuses';

export type SortMode = 'manual' | 'newest' | 'oldest';

export type ThemePreference = 'system' | 'light' | 'dark';

export interface Job {
  id: string;
  companyName: string;
  role: string;
  jobUrl?: string;
  resumeName?: string;
  appliedDate: string | null;
  salaryRange?: string;
  notes?: string;
  status: JobStatus;
  position: number;
  createdAt: string;
  updatedAt: string;
}

export interface AppSettings {
  theme: ThemePreference;
  sortMode: SortMode;
  hasSeenGuide: boolean;
}

export interface JobDraft {
  companyName: string;
  role: string;
  jobUrl: string;
  resumeName: string;
  appliedDate: string;
  salaryRange: string;
  notes: string;
  status: JobStatus;
}

export interface FieldErrors {
  companyName?: string;
  role?: string;
  jobUrl?: string;
  appliedDate?: string;
  status?: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
  persistent?: boolean;
}
