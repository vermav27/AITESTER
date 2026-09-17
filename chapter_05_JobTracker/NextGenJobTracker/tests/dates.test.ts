import { describe, expect, it } from 'vitest';
import {
  applyAutomaticAppliedDate,
  daysSinceApplied,
  formatAppliedAge,
  isFutureLocalDate,
  isValidLocalDate,
  todayLocalDate,
} from '../src/utils/dates';

describe('date utilities', () => {
  const now = new Date(2026, 8, 17, 8, 30);

  it('uses local calendar days', () => {
    expect(todayLocalDate(now)).toBe('2026-09-17');
    expect(daysSinceApplied('2026-09-16', now)).toBe(1);
    expect(formatAppliedAge(null, now)).toBe('Not applied');
  });

  it('validates real local dates and rejects future applied dates', () => {
    expect(isValidLocalDate('2026-02-29')).toBe(false);
    expect(isValidLocalDate('2024-02-29')).toBe(true);
    expect(isFutureLocalDate('2026-09-18', now)).toBe(true);
  });

  it('sets applied date only on first move out of Wishlist', () => {
    expect(applyAutomaticAppliedDate({ status: 'wishlist', appliedDate: null }, 'applied', now)).toBe(
      '2026-09-17',
    );
    expect(applyAutomaticAppliedDate({ status: 'wishlist', appliedDate: '2026-09-01' }, 'interview', now)).toBe(
      '2026-09-01',
    );
    expect(applyAutomaticAppliedDate({ status: 'applied', appliedDate: null }, 'interview', now)).toBeNull();
  });
});
