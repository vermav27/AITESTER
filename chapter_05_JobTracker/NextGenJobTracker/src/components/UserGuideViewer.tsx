import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { useEffect, useId, useRef, useState } from 'react';
import type {
  PDFDocumentLoadingTask,
  PDFDocumentProxy,
  PDFPageProxy,
  RenderTask,
} from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import { Modal } from './Modal';

interface UserGuideViewerProps {
  pdfUrl: string;
  onBack: () => void;
}

const MIN_ZOOM = 75;
const MAX_ZOOM = 175;
const ZOOM_STEP = 25;

function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error && error.message ? error.message : fallback;
}

export function UserGuideViewer({ pdfUrl, onBack }: UserGuideViewerProps) {
  const [documentProxy, setDocumentProxy] = useState<PDFDocumentProxy | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageCount, setPageCount] = useState(0);
  const [zoom, setZoom] = useState(100);
  const [containerWidth, setContainerWidth] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [renderedViewKey, setRenderedViewKey] = useState<string | null>(null);
  const [pageDescription, setPageDescription] = useState('');
  const [retryKey, setRetryKey] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pageContainerRef = useRef<HTMLDivElement>(null);
  const descriptionId = useId();

  useEffect(() => {
    const container = pageContainerRef.current;
    if (!container) {
      return;
    }

    const updateWidth = () => setContainerWidth(Math.max(1, Math.floor(container.clientWidth)));
    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let cancelled = false;
    let loadingTask: PDFDocumentLoadingTask | null = null;

    setDocumentProxy(null);
    setPageCount(0);
    setPageNumber(1);
    setLoadError(null);
    setRenderError(null);
    setRenderedViewKey(null);
    setPageDescription('');

    void (async () => {
      try {
        const pdfjs = await import('pdfjs-dist');
        if (cancelled) {
          return;
        }

        pdfjs.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;
        loadingTask = pdfjs.getDocument({ url: pdfUrl, isEvalSupported: false });
        const loadedDocument = await loadingTask.promise;
        if (cancelled) {
          return;
        }

        setDocumentProxy(loadedDocument);
        setPageCount(loadedDocument.numPages);
      } catch (error) {
        if (!cancelled) {
          setLoadError(getErrorMessage(error, 'The user guide could not be loaded.'));
        }
      }
    })();

    return () => {
      cancelled = true;
      if (loadingTask) {
        void loadingTask.destroy();
      }
    };
  }, [pdfUrl, retryKey]);

  useEffect(() => {
    if (!documentProxy || containerWidth === 0) {
      return;
    }

    let cancelled = false;
    let pageProxy: PDFPageProxy | null = null;
    let renderTask: RenderTask | null = null;

    setIsRendering(true);
    setRenderError(null);
    setRenderedViewKey(null);
    setPageDescription('');
    const viewKey = `${pageNumber}:${zoom}:${containerWidth}`;

    void (async () => {
      try {
        const canvas = canvasRef.current;
        if (!canvas) {
          return;
        }

        pageProxy = await documentProxy.getPage(pageNumber);
        if (cancelled) {
          return;
        }

        const unscaledViewport = pageProxy.getViewport({ scale: 1 });
        const fitScale = containerWidth / unscaledViewport.width;
        const viewport = pageProxy.getViewport({ scale: fitScale * (zoom / 100) });
        const outputScale = Math.max(1, window.devicePixelRatio || 1);
        const context = canvas.getContext('2d', { alpha: false });
        if (!context) {
          throw new Error('Canvas rendering is not supported in this browser.');
        }

        canvas.width = Math.floor(viewport.width * outputScale);
        canvas.height = Math.floor(viewport.height * outputScale);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        renderTask = pageProxy.render({
          canvas,
          canvasContext: context,
          viewport,
          transform: outputScale === 1 ? undefined : [outputScale, 0, 0, outputScale, 0, 0],
          background: '#ffffff',
        });

        const [, textContent] = await Promise.all([renderTask.promise, pageProxy.getTextContent()]);
        if (cancelled) {
          return;
        }

        const text = textContent.items
          .map((item) => ('str' in item ? item.str : ''))
          .join(' ')
          .replace(/\s+/g, ' ')
          .trim();
        setPageDescription(text || `User guide page ${pageNumber}.`);
        setRenderedViewKey(viewKey);
        setIsRendering(false);
      } catch (error) {
        if (!cancelled && !(error instanceof Error && error.name === 'RenderingCancelledException')) {
          setRenderError(getErrorMessage(error, 'This page could not be rendered.'));
          setIsRendering(false);
        }
      }
    })();

    return () => {
      cancelled = true;
      renderTask?.cancel();
      pageProxy?.cleanup();
    };
  }, [containerWidth, documentProxy, pageNumber, zoom]);

  const retry = () => setRetryKey((current) => current + 1);
  const pageLabel = pageCount > 0 ? `Page ${pageNumber} of ${pageCount}` : 'Loading pages';
  const currentViewKey = `${pageNumber}:${zoom}:${containerWidth}`;

  return (
    <Modal
      title="NextGen Job Tracker User Guide"
      onClose={onBack}
      closeLabel="Back to Help"
      size="xl"
      headerAction={
        <button type="button" className="btn-secondary h-9 px-3" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to Help
        </button>
      }
    >
      {loadError ? (
        <div className="grid min-h-80 place-items-center text-center" role="alert">
          <div className="max-w-md">
            <h3 className="text-lg font-semibold">Unable to open the user guide</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{loadError}</p>
            <div className="mt-5 flex flex-wrap justify-center gap-3">
              <button type="button" className="btn-primary" onClick={retry}>
                Retry
              </button>
              <button type="button" className="btn-secondary" onClick={onBack}>
                <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                Back to Help
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-950">
            <div className="flex items-center gap-2" aria-label="Page navigation">
              <button
                type="button"
                className="icon-button h-9 w-9"
                onClick={() => setPageNumber((current) => Math.max(1, current - 1))}
                disabled={!documentProxy || pageNumber <= 1}
                aria-label="Previous page"
                title="Previous page"
              >
                <ChevronLeft className="h-4 w-4" aria-hidden="true" />
              </button>
              <p className="min-w-24 text-center text-sm font-semibold" aria-live="polite">
                {pageLabel}
              </p>
              <button
                type="button"
                className="icon-button h-9 w-9"
                onClick={() => setPageNumber((current) => Math.min(pageCount, current + 1))}
                disabled={!documentProxy || pageNumber >= pageCount}
                aria-label="Next page"
                title="Next page"
              >
                <ChevronRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>

            <div className="flex items-center gap-2" aria-label="Zoom controls">
              <button
                type="button"
                className="icon-button h-9 w-9"
                onClick={() => setZoom((current) => Math.max(MIN_ZOOM, current - ZOOM_STEP))}
                disabled={!documentProxy || zoom <= MIN_ZOOM}
                aria-label="Zoom out"
                title="Zoom out"
              >
                <ZoomOut className="h-4 w-4" aria-hidden="true" />
              </button>
              <button
                type="button"
                className="btn-secondary h-9 min-w-20 px-3"
                onClick={() => setZoom(100)}
                disabled={!documentProxy || zoom === 100}
                aria-label={`Reset zoom, currently ${zoom}%`}
                title="Reset zoom"
              >
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
                {zoom}%
              </button>
              <button
                type="button"
                className="icon-button h-9 w-9"
                onClick={() => setZoom((current) => Math.min(MAX_ZOOM, current + ZOOM_STEP))}
                disabled={!documentProxy || zoom >= MAX_ZOOM}
                aria-label="Zoom in"
                title="Zoom in"
              >
                <ZoomIn className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </div>

          <div
            ref={pageContainerRef}
            className="relative min-h-80 max-h-[calc(90vh-190px)] overflow-auto rounded-md border border-slate-200 bg-slate-100 p-4 dark:border-slate-700 dark:bg-slate-950"
            aria-busy={
              !renderError && (!documentProxy || renderedViewKey !== currentViewKey)
            }
          >
            {!documentProxy ? (
              <div className="grid min-h-72 place-items-center" role="status">
                <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  Loading user guide...
                </p>
              </div>
            ) : (
              <div
                className="mx-auto w-max max-w-none overflow-hidden rounded-sm bg-white shadow-lg"
                role="img"
                aria-label={`User guide page ${pageNumber} of ${pageCount}`}
                aria-describedby={descriptionId}
              >
                <canvas ref={canvasRef} className="block bg-white" aria-hidden="true" />
              </div>
            )}

            {documentProxy && isRendering ? (
              <div
                className="pointer-events-none absolute inset-0 grid place-items-center bg-slate-100/70 dark:bg-slate-950/70"
                role="status"
              >
                <p className="rounded-md bg-white px-3 py-2 text-sm font-medium shadow-sm dark:bg-slate-900">
                  Rendering page...
                </p>
              </div>
            ) : null}

            {renderError ? (
              <div className="absolute inset-0 grid place-items-center bg-slate-100 p-6 text-center dark:bg-slate-950" role="alert">
                <div className="max-w-md">
                  <h3 className="font-semibold">Unable to display this page</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {renderError}
                  </p>
                  <div className="mt-4 flex flex-wrap justify-center gap-3">
                    <button type="button" className="btn-primary" onClick={retry}>
                      Retry
                    </button>
                    <button type="button" className="btn-secondary" onClick={onBack}>
                      <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                      Back to Help
                    </button>
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <p id={descriptionId} className="sr-only">
            {pageDescription}
          </p>
        </div>
      )}
    </Modal>
  );
}
