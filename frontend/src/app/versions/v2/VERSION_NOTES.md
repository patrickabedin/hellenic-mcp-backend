# v2 — Landing Page Rebuild

**Date:** 2026-03-28
**Deployed:** https://hellenic-google-ads-mcp-next.vercel.app

## Changes from v1

### 1. Hero — Complete Redesign
- **Removed** the ChatDemo from the hero (too heavy above the fold)
- **Added** a CSS/HTML product screenshot mockup — dark browser window frame with:
  - 3 metric cards: CTR 4.2%, ROAS 6.8x, Spend $12,400
  - Fake campaign performance bar chart
  - AI chat overlay bubble: "Pause all campaigns under $2 ROAS"
- Headline, badge, subtext, and CTA buttons preserved
- Works marquee stays below the hero
- All old blue `#0042BF` → brand blue `#3B82F6`

### 2. ChatDemo — Moved to Own Section
- **New section:** "See It In Action" (between UseCases and Tools)
- Full-width dark card, centered, max-w-3xl
- Title: "Ask anything. Get results instantly."
- 3 example prompt chips above the chat:
  - "Pause underperforming campaigns"
  - "Show me ROAS by campaign"
  - "Increase budget for top performers"
- ChatDemo animated component placed inside

### 3. Tools Section — Visual Upgrade
- **Old:** plain numbered list with blue number prefix
- **New:** 3-column card grid (responsive: 1 col → 2 col → 3 col)
- Each card has:
  - Lucide SVG icon in a blue-tinted circle
  - Tool name (monospace font)
  - One-line description
- Cards: `bg-[#111111]`, `border-white/[0.06]`, hover: `border-white/[0.12]` + slight lift
- All 25 tools kept with icons assigned

### 4. Social Proof Section — NEW
- Title: "Trusted by agencies and marketers"
- 3 testimonial cards with realistic quotes from:
  - Marcus Lindström (Head of Performance, Nordic Digital Agency)
  - Sarah Chen (Growth Marketing Lead, ScaleUp Commerce)
  - Dimitris Papadopoulos (Founder & CEO, Aegean Eats)
- Each card: quote, name, role, company, colored circle avatar with initials
- Dark cards, same style as Tools

### 5. Stats Bar — NEW
- Added between Hero and UseCases
- 4 stats: "25 Tools" | "500+" | "Free Forever" | "100% Open Source"
- Animated number counting on scroll (IntersectionObserver + framer-motion)

### 6. Header — hellenicAI Logo
- **Replaced** Zap icon + "Google Ads MCP" text with:
  - "hellenic" in white font-bold + "AI" in `#3B82F6` (blue)
  - "Google Ads MCP" subtitle in muted text
- CTA button updated to brand blue

### 7. Footer — Expanded
- **Added:** Documentation link
- **Added:** hellenicAI.com link
- **Added:** "Built by Hellenic Technologies" with link to hellenictechnologies.com
- Logo restyled to match header (hellenicAI branding)

### 8. Brand Consistency
- All `#0042BF` replaced with `#3B82F6` (brand blue from brand guide)
- CSS variables updated in globals.css
- Tailwind config updated with brand color aliases
- Typewriter cursor color updated
- Radial glow updated to use new blue

### 9. Components Changed
| Component | Status |
|---|---|
| `Header.tsx` | Modified — new logo |
| `Hero.tsx` | Rewritten — product mockup instead of ChatDemo |
| `StatsBar.tsx` | NEW — animated stat counters |
| `SeeItInAction.tsx` | NEW — ChatDemo wrapper with prompt chips |
| `ChatDemo.tsx` | Modified — colors updated to `#3B82F6` |
| `Tools.tsx` | Rewritten — card grid with icons |
| `SocialProof.tsx` | NEW — testimonial cards |
| `Footer.tsx` | Rewritten — expanded links |
| `page.tsx` | Rewritten — new section order |
| `globals.css` | Modified — color variables updated |
| `tailwind.config.ts` | Modified — brand color aliases added |

### 10. Preserved (unchanged from v1)
- `UseCases.tsx` — kept as-is
- `HowItWorks.tsx` — kept as-is
- `ManagedService.tsx` — kept as-is
- `CTA.tsx` — kept as-is
- `FAQ.tsx` — kept as-is
- `Works.tsx` — kept as-is
- v1 archive (`src/app/versions/v1/`, `src/components/versions/v1/`) — untouched
