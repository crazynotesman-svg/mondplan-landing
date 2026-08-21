# MondPlan - Landing Page

Static landing page for **MondPlan - Biodynamic Moon Calendar (月相日历)**, built with
plain HTML + Tailwind CSS. Designed for GitHub tracking and Cloudflare Pages deployment
(zero build step on the edge).

- App Store ID: `6758746304`
- App Store URL: `https://apps.apple.com/app/id6758746304`

## Project Structure

```
mondplan/
├── index.html          # Main landing page (hero + interactive moon + features + FAQ)
├── privacy.html        # App Store compliant privacy policy
├── support.html        # Support page (required by App Store)
├── llms.txt            # Short plain-text summary for AI crawlers (Perplexity, ChatGPT, Claude)
├── llms-full.txt       # Full plain-text reference (FAQ + all features) for AI crawlers
├── robots.txt          # Allows standard + AI crawlers (GPTBot, PerplexityBot, ClaudeBot...)
├── sitemap.xml         # XML sitemap (index / privacy / support)
├── _headers            # Cloudflare Pages headers (security + charset/cache for crawler files)
├── README.md           # This file
├── assets/
│   ├── tailwind.css    # Compiled, minified Tailwind CSS (committed to the repo)
│   ├── badge-appstore.svg  # Official Apple "Download on the App Store" badge
│   ├── favicon.svg     # Moon favicon
│   ├── apple-touch-icon.png # 180x180 iOS home-screen icon
│   └── og-image.png    # Open Graph share image (1200x630)
├── src/
│   └── input.css       # Tailwind source (brand tokens + custom styles)
├── scripts/
│   └── generate_og.py  # Regenerates og-image.png (Pillow)
└── package.json        # Dev-only: Tailwind build pipeline
```

## Local Preview

Because the compiled CSS is committed, the site runs with zero build:

```bash
# Option A: any static server (recommended for testing)
python3 -m http.server 8080
# open http://localhost:8080

# Option B: just open index.html directly in a browser
open index.html
```

## Rebuilding CSS (only if you change styles)

Tailwind is used only at build time; the runtime page is a single small CSS file.

```bash
npm install        # once
npm run build:css  # outputs minified assets/tailwind.css
```

## Before Going Live - Replace Placeholders

| Item | Current value | Action |
|------|---------------|--------|
| Canonical domain | `https://mondplan.100ideas.net/` | Replace with your final domain (search all files: `index.html`, `privacy.html`, `support.html`, `llms.txt`, `llms-full.txt`, `robots.txt`, `sitemap.xml`) |
| `og:image` | `assets/og-image.png` | Regenerate with your final branding, then update the absolute URL in `index.html` |
| Support email | `support@100ideas.net` | Replace with the real support address if different |
| `aggregateRating` | *(omitted)* | Add to the SoftwareApplication JSON-LD in `index.html` only once the App Store shows real review data - never publish a fabricated rating |

## Deploy to GitHub

```bash
cd mondplan

# 1. Init and commit
git init
git add .
git commit -m "feat: MondPlan landing page (SEO + GEO, static)"

# 2. Create a repository on GitHub (github.com -> New repository, e.g. "mondplan-landing")

# 3. Link and push
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/mondplan-landing.git
git push -u origin main
```

## Connect Cloudflare Pages

1. Go to **Cloudflare Dashboard** -> **Workers & Pages** -> **Create** -> **Pages** -> **Connect to Git**.
2. Pick the `mondplan-landing` repository.
3. Build settings (all fields as follows - there is no build step):
   - **Framework preset:** `None`
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (the repository root)
4. Click **Save and Deploy**. The site goes live at `<project>.pages.dev`.
5. *(Optional)* Add a custom domain under **Custom domains** (e.g. `mondplan.100ideas.net`) and set the matching `CNAME` DNS record.

No `npx` or Node is required on Cloudflare - `assets/tailwind.css` is already committed.

## Post-Deploy Checklist

- [ ] `https://<domain>/` returns 200 and shows the hero
- [ ] `https://<domain>/llms.txt` is served as `text/plain`
- [ ] `https://<domain>/llms-full.txt` is served as `text/plain`
- [ ] `https://<domain>/robots.txt` shows `Sitemap:` line
- [ ] `https://<domain>/sitemap.xml` validates (Google Search Console -> Sitemaps)
- [ ] `apple-itunes-app` meta tag present in `<head>` (enables the Smart App Banner)
- [ ] `_headers` is picked up automatically by Cloudflare Pages (no config needed)
- [ ] Submit the sitemap in Google Search Console and Bing Webmaster Tools
- [ ] Confirm all `https://apps.apple.com/app/id6758746304` links open the App Store

## Notes

- **Moon phase math**: the interactive widget uses the standard synodic-cycle
  approximation (Jean Meeus, *Astronomical Algorithms*), with the reference new moon at
  `2000-01-06 18:14 UTC` (JD 2451550.1) and a cycle of `29.530588853` days. The "Today"
  button computes the real current phase from the device date.
- **SEO/GEO**: page ships `MobileApplication` + `WebPage` + `FAQPage` JSON-LD, Open Graph,
  Twitter Card, canonical URLs, semantic HTML5, a structured Quick Facts entity table, and
  both `llms.txt` / `llms-full.txt` at the root for AI search engines. `robots.txt` explicitly
  allows GPTBot, PerplexityBot, ClaudeBot, OAI-SearchBot, Google-Extended, Applebot,
  Amazonbot, cohere-ai, Meta-ExternalAgent, Bytespider, PetalBot and more.

## License

Content and design (c) 2026 100BadIdeas. The App Store badge is Apple's official asset.
