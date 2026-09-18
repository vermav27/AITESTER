import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Dashboard } from '../src/components/Dashboard';
import { makeJob } from './testHelpers';

describe('Dashboard', () => {
  it('renders live metrics, an accessible chart and outcome company details', () => {
    const jobs = [
      makeJob({ id: 'wishlist', status: 'wishlist', companyName: 'Northwind', role: 'QA Lead' }),
      makeJob({ id: 'applied', status: 'applied', companyName: 'Globex', role: 'SDET' }),
      makeJob({ id: 'offer', status: 'offer', companyName: 'Acme', role: 'Senior QA' }),
      makeJob({ id: 'rejected', status: 'rejected', companyName: 'Initech', role: 'Test Engineer' }),
    ];

    render(<Dashboard jobs={jobs} />);

    expect(screen.getByRole('article', { name: 'Total number of jobs: 4' })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Wishlisted: 1' })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Applied: 1' })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Offer: 1' })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Rejected: 1' })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /^Job status distribution/ })).toBeInTheDocument();

    const offerSection = screen.getByRole('region', { name: 'Offer' });
    expect(within(offerSection).getByText('Acme')).toBeInTheDocument();
    expect(within(offerSection).getByText('Senior QA')).toBeInTheDocument();

    const rejectedSection = screen.getByRole('region', { name: 'Rejected' });
    expect(within(rejectedSection).getByText('Initech')).toBeInTheDocument();
    expect(within(rejectedSection).getByText('Test Engineer')).toBeInTheDocument();
  });

  it('renders a complete zero-data state', () => {
    render(<Dashboard jobs={[]} />);

    expect(screen.getByRole('article', { name: 'Total number of jobs: 0' })).toBeInTheDocument();
    expect(screen.getAllByRole('article')).toHaveLength(7);
    expect(screen.getByText('No application data yet')).toBeInTheDocument();
    expect(screen.getByText('No offers yet')).toBeInTheDocument();
    expect(screen.getByText('No rejected applications')).toBeInTheDocument();
  });
});
