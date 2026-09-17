# Brand Assets

The app uses platform marks only to identify the source of a user-saved job link. It does not imply partnership, endorsement, sponsorship, or data integration with any job platform.

No runtime favicon service, hotlinked logo, or remote logo lookup is used.

## Included Simple Icons Assets

These icons are imported from the installed `simple-icons` npm package and rendered from local bundled code through tree-shaken imports in `src/platforms/registry.ts`.

| Platform | Simple Icons title | Hex colour | Source metadata from package | Guidelines metadata from package |
|---|---|---:|---|---|
| LinkedIn | LinkedIn | `#0A66C2` | `https://brand.linkedin.com` | `https://brand.linkedin.com/policies` |
| Indeed | Indeed | `#003A9B` | `https://indeed.design/resources` | Not provided by installed icon metadata |
| Glassdoor | Glassdoor | `#00A162` | `https://www.glassdoor.com/about/newsroom` | `https://www.glassdoor.com/about/newsroom` |
| Wellfound | Wellfound | `#000000` | `https://wellfound.com/logo` | Not provided by installed icon metadata |

Simple Icons package files inspected locally:

- `node_modules/simple-icons/LICENSE.md`
- `node_modules/simple-icons/DISCLAIMER.md`

The package license file is CC0 1.0 Universal. The disclaimer notes that users should check individual icon metadata, brand guidelines and trademark considerations. Trademarks remain with their owners.

## Fallback Badges

For platforms where a verified icon was not available in the installed Simple Icons package during this implementation, the app uses a simple text initial badge rather than inventing or approximating a trademarked logo.

| Platform | Badge |
|---|---|
| Naukri | `N` initial badge |
| Foundit | `F` initial badge |
| Instahyre | `I` initial badge |
| Cutshort | `C` initial badge |
| Hirist | `H` initial badge |
| IIMJobs | `IJ` initial badge |

Unknown job URLs use a generic external-link icon and the detected hostname as the accessible source name.
