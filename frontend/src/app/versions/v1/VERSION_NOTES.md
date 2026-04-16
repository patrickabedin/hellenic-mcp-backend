# v1 — Original Build (2026-03-27)

**Status:** Preserved — do not delete
**Deployed to:** Vercel staging + Cloudflare Pages (commit a557079)

## What this version is
The first full build of the Google Ads MCP landing page.
- 21 components, 10 sections
- Dark Linear-inspired theme (#09090B base)
- Blue CTA band (#0074e0 → #005bb5)
- framer-motion scroll animations
- 22-tool numbered grid
- ChatDemo animated typewriter
- Works marquee of AI assistants

## Known issues at time of archival
- ChatDemo transition animation was rough
- "Works" label on marquee was unclear
- Tool count in heading said 11 (should be 22)
- Some animations were janky on mobile

## To restore v1
Copy all files from this directory back to:
- `src/app/page.tsx`
- `src/app/globals.css`
- `src/app/layout.tsx`
- `src/components/*.tsx` (from versions/v1/)
