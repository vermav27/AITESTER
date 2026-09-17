const SAFE_PROTOCOLS = new Set(['http:', 'https:']);
const TRACKING_PARAMS = new Set([
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
  'trk',
  'trackingId',
]);

export function parseHttpUrl(value: string): URL | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  try {
    const url = new URL(trimmed);
    return SAFE_PROTOCOLS.has(url.protocol) ? url : null;
  } catch {
    return null;
  }
}

export function validateOptionalHttpUrl(value: string): string | undefined {
  if (!value.trim()) {
    return undefined;
  }

  return parseHttpUrl(value)
    ? undefined
    : 'Enter a valid http:// or https:// job link.';
}

export function normalizeHostname(hostname: string): string {
  const lower = hostname.toLowerCase();
  return lower.startsWith('www.') ? lower.slice(4) : lower;
}

export function getHostname(value: string): string | null {
  const parsed = parseHttpUrl(value);
  return parsed ? normalizeHostname(parsed.hostname) : null;
}

export function hostnameMatchesDomain(hostname: string, domain: string): boolean {
  const normalizedHost = normalizeHostname(hostname);
  const normalizedDomain = normalizeHostname(domain);
  return normalizedHost === normalizedDomain || normalizedHost.endsWith(`.${normalizedDomain}`);
}

export function normalizeUrlForComparison(value: string): string | null {
  const parsed = parseHttpUrl(value);
  if (!parsed) {
    return null;
  }

  parsed.hostname = normalizeHostname(parsed.hostname);
  parsed.hash = '';

  for (const key of [...parsed.searchParams.keys()]) {
    if (TRACKING_PARAMS.has(key)) {
      parsed.searchParams.delete(key);
    }
  }

  if (parsed.pathname !== '/') {
    parsed.pathname = parsed.pathname.replace(/\/+$/, '');
  }

  if (parsed.pathname === '/') {
    parsed.pathname = '';
  }

  return parsed.toString();
}
