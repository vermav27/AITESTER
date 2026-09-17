import { siGlassdoor, siIndeed, siLinkedin, siWellfound } from 'simple-icons/icons';
import { ExternalLink } from 'lucide-react';
import type { ComponentType, SVGProps } from 'react';
import { getHostname, hostnameMatchesDomain } from '../utils/urls';

type SimpleIconDefinition = {
  title: string;
  path: string;
  hex: string;
};

export type PlatformId =
  | 'linkedin'
  | 'naukri'
  | 'indeed'
  | 'glassdoor'
  | 'foundit'
  | 'wellfound'
  | 'instahyre'
  | 'cutshort'
  | 'hirist'
  | 'iimjobs';

export type PlatformIcon =
  | { type: 'simple-icons'; icon: SimpleIconDefinition }
  | { type: 'initials'; initials: string; color: string };

export interface PlatformDefinition {
  id: PlatformId;
  name: string;
  hostnames: string[];
  icon: PlatformIcon;
  externalLinkLabel: string;
}

export interface DetectedSource {
  id: PlatformId | 'unknown';
  name: string;
  hostname: string;
  icon: PlatformIcon | { type: 'generic'; component: ComponentType<SVGProps<SVGSVGElement>> };
  externalLinkLabel: string;
}

export const PLATFORM_REGISTRY: PlatformDefinition[] = [
  {
    id: 'linkedin',
    name: 'LinkedIn',
    hostnames: ['linkedin.com', 'lnkd.in'],
    icon: { type: 'simple-icons', icon: siLinkedin },
    externalLinkLabel: 'Open job on LinkedIn',
  },
  {
    id: 'naukri',
    name: 'Naukri',
    hostnames: ['naukri.com'],
    icon: { type: 'initials', initials: 'N', color: '#2451A6' },
    externalLinkLabel: 'Open job on Naukri',
  },
  {
    id: 'indeed',
    name: 'Indeed',
    hostnames: ['indeed.com'],
    icon: { type: 'simple-icons', icon: siIndeed },
    externalLinkLabel: 'Open job on Indeed',
  },
  {
    id: 'glassdoor',
    name: 'Glassdoor',
    hostnames: ['glassdoor.com', 'glassdoor.co.in'],
    icon: { type: 'simple-icons', icon: siGlassdoor },
    externalLinkLabel: 'Open job on Glassdoor',
  },
  {
    id: 'foundit',
    name: 'Foundit',
    hostnames: ['foundit.in'],
    icon: { type: 'initials', initials: 'F', color: '#5F2EEA' },
    externalLinkLabel: 'Open job on Foundit',
  },
  {
    id: 'wellfound',
    name: 'Wellfound',
    hostnames: ['wellfound.com'],
    icon: { type: 'simple-icons', icon: siWellfound },
    externalLinkLabel: 'Open job on Wellfound',
  },
  {
    id: 'instahyre',
    name: 'Instahyre',
    hostnames: ['instahyre.com'],
    icon: { type: 'initials', initials: 'I', color: '#0E7C7B' },
    externalLinkLabel: 'Open job on Instahyre',
  },
  {
    id: 'cutshort',
    name: 'Cutshort',
    hostnames: ['cutshort.io'],
    icon: { type: 'initials', initials: 'C', color: '#E15634' },
    externalLinkLabel: 'Open job on Cutshort',
  },
  {
    id: 'hirist',
    name: 'Hirist',
    hostnames: ['hirist.tech'],
    icon: { type: 'initials', initials: 'H', color: '#475569' },
    externalLinkLabel: 'Open job on Hirist',
  },
  {
    id: 'iimjobs',
    name: 'IIMJobs',
    hostnames: ['iimjobs.com'],
    icon: { type: 'initials', initials: 'IJ', color: '#0F766E' },
    externalLinkLabel: 'Open job on IIMJobs',
  },
];

export function detectPlatform(jobUrl?: string): DetectedSource | null {
  if (!jobUrl) {
    return null;
  }

  const hostname = getHostname(jobUrl);
  if (!hostname) {
    return null;
  }

  const platform = PLATFORM_REGISTRY.find((candidate) =>
    candidate.hostnames.some((domain) => hostnameMatchesDomain(hostname, domain)),
  );

  if (!platform) {
    return {
      id: 'unknown',
      name: hostname,
      hostname,
      icon: { type: 'generic', component: ExternalLink },
      externalLinkLabel: `Open job on ${hostname}`,
    };
  }

  return {
    id: platform.id,
    name: platform.name,
    hostname,
    icon: platform.icon,
    externalLinkLabel: platform.externalLinkLabel,
  };
}
