# Google Ads MCP Landing Page — Deploy Guide

> ⚠️ CRITICAL: CF Pages uses **direct upload** (no GitHub auto-deploy). Git pushes to `patrickabedin/landing-pages` do NOT trigger rebuilds. You MUST use `wrangler pages deploy`.

## Architecture

| Component | Details |
|---|---|
| **Live URL** | `https://google-ads-mcp.hellenicai.com` |
| **CF Pages project** | `google-ads-mcp` |
| **Deploy method** | `wrangler pages deploy` (direct upload) |
| **Source repo** | `patrickabedin/landing-pages` → `google-ads-mcp/` subfolder |
| **Local workspace** | `/root/.openclaw/workspace/hellenic-google-ads-mcp-next/` |
| **Framework** | Next.js 14 static export (`output: 'export'`) |

## Deploy Steps (every time you make changes)

```bash
# 1. Make changes in the Next.js workspace
cd /root/.openclaw/workspace/hellenic-google-ads-mcp-next/

# 2. Build the static export
npm run build
# Output goes to: out/

# 3. Clone/update the landing-pages repo
cd /tmp
rm -rf landing-pages
git clone https://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@github.com/patrickabedin/landing-pages.git
cd landing-pages

# 4. Copy the new build into the google-ads-mcp subfolder
rm -rf google-ads-mcp
cp -r /root/.openclaw/workspace/hellenic-google-ads-mcp-next/out/ google-ads-mcp

# 5. Push to GitHub (for source control — does NOT auto-deploy CF Pages)
git add -A
git commit -m "deploy: update google-ads-mcp landing page"
git push origin main

# 6. Deploy to CF Pages via wrangler (THIS is what actually updates the live site)
cd /tmp/landing-pages/google-ads-mcp
npx wrangler pages deploy . --project-name=google-ads-mcp --branch=main

# 7. Verify live
curl -s -o /dev/null -w "%{http_code}" https://google-ads-mcp.hellenicai.com
# Should return 200
```

## Why Git Push Alone Doesn't Work

CF Pages project `google-ads-mcp` has `source: null` — it was set up as a **direct upload** project, not connected to a GitHub repo. This means:
- ✅ `wrangler pages deploy` → updates the live site
- ❌ `git push` → updates the repo only, CF Pages ignores it

## Verify Deploy Worked

```bash
# Check CSS hash changed (new build = new hash)
curl -s https://google-ads-mcp.hellenicai.com | grep -o 'css/[a-f0-9]*.css'

# Check Tailwind is present in CSS (should start with --tw-border-spacing)
CSS_HASH=$(curl -s https://google-ads-mcp.hellenicai.com | grep -o 'css/[a-f0-9]*.css' | head -1)
curl -s "https://google-ads-mcp.hellenicai.com/_next/static/$CSS_HASH" | head -c 100
```

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| Old CSS still loading | Forgot to run `wrangler pages deploy` | Run step 6 above |
| Page blank / opacity:0 | Framer Motion JS not running | CSS override in `globals.css` handles this |
| Tailwind classes not working | Old CSS without Tailwind | Rebuild + redeploy |
| `wrangler` not found | Not installed | `npm install -g wrangler` |

## File Structure

```
hellenic-google-ads-mcp-next/
├── src/
│   ├── app/
│   │   ├── page.tsx          ← Main landing page
│   │   ├── layout.tsx        ← Root layout
│   │   └── globals.css       ← Global styles + Tailwind + Framer fix
│   └── components/           ← Section components
├── next.config.ts            ← output: 'export' + trailingSlash: true
├── tailwind.config.ts
├── package.json
└── out/                      ← Built static export (gitignored)
```

## Wrangler Auth

Wrangler uses the Cloudflare API token stored in the environment. If it prompts for login:
```bash
npx wrangler login
# Or set: export CLOUDFLARE_API_TOKEN=<token>
```
