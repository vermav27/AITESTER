import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { HelpGuide } from '../src/components/HelpGuide';

const pdfMocks = vi.hoisted(() => ({
  cancel: vi.fn(),
  cleanup: vi.fn(),
  documentDestroy: vi.fn(),
  getDocument: vi.fn(),
  getPage: vi.fn(),
  loadingDestroy: vi.fn(),
  render: vi.fn(),
}));

vi.mock('pdfjs-dist', () => ({
  GlobalWorkerOptions: { workerSrc: '' },
  getDocument: pdfMocks.getDocument,
}));

class ImmediateResizeObserver implements ResizeObserver {
  constructor(private readonly callback: ResizeObserverCallback) {}

  observe(target: Element) {
    this.callback([], this);
    void target;
  }

  disconnect() {}

  unobserve() {}
}

function configureSuccessfulPdf() {
  pdfMocks.render.mockReturnValue({
    cancel: pdfMocks.cancel,
    promise: Promise.resolve(),
  });
  pdfMocks.getPage.mockImplementation((pageNumber: number) =>
    Promise.resolve({
      cleanup: pdfMocks.cleanup,
      getTextContent: () => Promise.resolve({ items: [{ str: `Accessible text for page ${pageNumber}` }] }),
      getViewport: ({ scale }: { scale: number }) => ({ height: 842 * scale, width: 595 * scale }),
      render: pdfMocks.render,
    }),
  );
  pdfMocks.getDocument.mockReturnValue({
    destroy: pdfMocks.loadingDestroy,
    promise: Promise.resolve({
      destroy: pdfMocks.documentDestroy,
      getPage: pdfMocks.getPage,
      numPages: 5,
    }),
  });
}

function HelpHarness() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>
        Open Help
      </button>
      {open ? <HelpGuide onClose={() => setOpen(false)} /> : null}
    </>
  );
}

describe('Help user guide viewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    configureSuccessfulPdf();
    vi.stubGlobal('ResizeObserver', ImmediateResizeObserver);
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(720);
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      {} as CanvasRenderingContext2D,
    );
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
      callback(0);
      return 1;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('replaces Help with one accessible viewer and exposes no file actions', async () => {
    const user = userEvent.setup();
    render(<HelpGuide onClose={vi.fn()} />);

    const helpDialog = screen.getByRole('dialog', { name: 'How to use this tracker' });
    await user.click(within(helpDialog).getByRole('button', { name: 'View User Guide' }));

    const viewer = await screen.findByRole('dialog', {
      name: 'NextGen Job Tracker User Guide',
    });
    expect(screen.getAllByRole('dialog')).toHaveLength(1);
    expect(screen.queryByRole('dialog', { name: 'How to use this tracker' })).not.toBeInTheDocument();
    expect(await within(viewer).findByText('Page 1 of 5')).toBeInTheDocument();
    expect(within(viewer).getByRole('button', { name: 'Previous page' })).toBeDisabled();
    expect(within(viewer).getByRole('button', { name: 'Next page' })).toBeEnabled();
    expect(within(viewer).queryByRole('link')).not.toBeInTheDocument();
    expect(within(viewer).queryByText(/download|print|open in new tab/i)).not.toBeInTheDocument();
    expect(
      await within(viewer).findByRole('img', { name: 'User guide page 1 of 5' }),
    ).toHaveAccessibleDescription('Accessible text for page 1');
  });

  it('navigates all pages and enforces the zoom boundaries', async () => {
    const user = userEvent.setup();
    render(<HelpGuide onClose={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: 'View User Guide' }));

    const viewer = await screen.findByRole('dialog', {
      name: 'NextGen Job Tracker User Guide',
    });
    const next = within(viewer).getByRole('button', { name: 'Next page' });
    for (let page = 2; page <= 5; page += 1) {
      await user.click(next);
      expect(within(viewer).getByText(`Page ${page} of 5`)).toBeInTheDocument();
    }
    expect(next).toBeDisabled();

    const zoomIn = within(viewer).getByRole('button', { name: 'Zoom in' });
    await user.click(zoomIn);
    await user.click(zoomIn);
    await user.click(zoomIn);
    expect(within(viewer).getByRole('button', { name: 'Reset zoom, currently 175%' })).toBeEnabled();
    expect(zoomIn).toBeDisabled();

    const zoomOut = within(viewer).getByRole('button', { name: 'Zoom out' });
    await user.click(zoomOut);
    await user.click(zoomOut);
    await user.click(zoomOut);
    await user.click(zoomOut);
    expect(within(viewer).getByRole('button', { name: 'Reset zoom, currently 75%' })).toBeEnabled();
    expect(zoomOut).toBeDisabled();
  });

  it('returns to Help on Escape and restores focus after Help closes', async () => {
    const user = userEvent.setup();
    render(<HelpHarness />);

    const launcher = screen.getByRole('button', { name: 'Open Help' });
    await user.click(launcher);
    await user.click(screen.getByRole('button', { name: 'View User Guide' }));
    await screen.findByRole('dialog', { name: 'NextGen Job Tracker User Guide' });

    await user.keyboard('{Escape}');
    expect(await screen.findByRole('dialog', { name: 'How to use this tracker' })).toBeInTheDocument();
    expect(screen.getAllByRole('dialog')).toHaveLength(1);

    await user.click(screen.getByText('Close', { selector: 'button' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(launcher).toHaveFocus();
  });

  it('shows recovery actions when PDF loading fails and retries successfully', async () => {
    const user = userEvent.setup();
    pdfMocks.getDocument.mockImplementationOnce(() => ({
      destroy: pdfMocks.loadingDestroy,
      promise: Promise.reject(new Error('Guide unavailable')),
    }));
    render(<HelpGuide onClose={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'View User Guide' }));
    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText('Guide unavailable')).toBeInTheDocument();
    expect(within(alert).getByRole('button', { name: 'Back to Help' })).toBeInTheDocument();

    await user.click(within(alert).getByRole('button', { name: 'Retry' }));
    await waitFor(() => expect(screen.getByText('Page 1 of 5')).toBeInTheDocument());
  });

  it('shows recovery actions when page rendering fails', async () => {
    const user = userEvent.setup();
    pdfMocks.render.mockImplementationOnce(() => ({
      cancel: pdfMocks.cancel,
      promise: Promise.reject(new Error('Page unavailable')),
    }));
    render(<HelpGuide onClose={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'View User Guide' }));
    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText('Page unavailable')).toBeInTheDocument();
    expect(within(alert).getByRole('button', { name: 'Back to Help' })).toBeInTheDocument();

    await user.click(within(alert).getByRole('button', { name: 'Retry' }));
    await waitFor(() =>
      expect(screen.getByRole('img', { name: 'User guide page 1 of 5' })).toHaveAccessibleDescription(
        'Accessible text for page 1',
      ),
    );
  });
});
