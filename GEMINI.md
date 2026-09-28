# Local Website Development & SEO Guidelines

0. **Mandatory Intake Before Website Creation**:
   - Before creating any website or generating pages, you MUST ask the user for these specific inputs:
     1. Website / Business Name
     2. Website Address (Physical Address / Service Area & Domain URL)
     3. Website Phone Number
     4. Category (Primary GMB Category / Business Niche)
     5. Operating Hours
     6. Target Keywords
     7. Competitor URLs
   - Do NOT generate custom site pages until these details are provided.

1. **Website Architecture & Performance**:
   - Mobile-first, responsive layouts.
   - Core Web Vitals compliance (LCP < 2.5s, CLS < 0.1, INP < 200ms).
   - Inlined critical CSS, deferred non-critical JS, and self-hosted/preconnected fonts.
   - **MANDATORY ASSET EXISTENCE**: `assets/css/styles.css` and `assets/js/main.js` MUST always be generated, written to disk, and verified before deployment. A site must NEVER be deployed without full CSS and JS files.
   - **STRICT SVG CONSTRAINTS**: EVERY `<svg>` element (brand logo, trust items, buttons, footer, mobile bar) MUST have explicit inline `width="..." height="..."` attributes in HTML AND be protected with inlined critical CSS in `<head>` (e.g. `.brand-logo svg { width: 34px !important; height: 34px !important; max-width: 34px; max-height: 34px; }`). SVGs must NEVER rely solely on external stylesheets to prevent any flash of unstyled content (FOUC) or oversized icons.

2. **Mobile Conversion & CTAs**:
   - Every local service page must feature high-converting click-to-call links (`tel:+...`) with accessible touch targets (> 48px height).
   - Use the mobile sticky call bar pattern on viewports under 768px.
   - Include GA4 `dataLayer.push` tracking handlers on call buttons.

3. **Page Structure & E-E-A-T**:
   - Follow the high-trust layout blueprint for core pages (Hero, Quantified Proof, Real Team/Founders, Accreditations/Licenses, Local Reviews, and Clear CTAs).

4. **Technical & On-Page SEO**:
   - Single semantic `<h1>` tag with primary keyword and geo-modifier.
   - Logical heading hierarchy (`<h2>` -> `<h3>`) without skipping levels.
   - All `<img>` tags must have explicit `width`, `height`, descriptive `alt` text, and `loading="lazy"` (except the hero image which uses `fetchpriority="high"`).
   - Valid JSON-LD Schema markup (`LocalBusiness`, `RoofingContractor`, etc.) embedded on every relevant template.

5. **Automated Search Console, Sitemaps & Deployment**:
   - Every site created MUST include a canonical `sitemap.xml` (with clean URLs) and `robots.txt` pointing to that sitemap.
   - Cloudflare Pages custom domains, DNS CNAMEs, and edge URL rewrite rules must be configured.
   - Cloudflare Email Routing must be auto-enabled, forwarding `info@` and catch-all `*@` to `anis@agesoftsolutions.com`.
   - Spaceship nameservers must be synced to Cloudflare.
   - Google Search Console site addition and sitemap submission MUST be performed programmatically via `../scripts/gsc_manager.py` using the service account key in `../config.json`.

6. **Full Autonomous Pipeline (Zero Mid-Process Questioning & No Planning Pause)**:
   - As soon as the 7 mandatory intake details are provided, do NOT pause for planning approvals or ask clarifying questions.
   - Execute the entire build and deployment pipeline end-to-end in one continuous flow:
     1. Sync Spaceship & Cloudflare zone.
     2. Generate clean HTML/CSS/JS, schema, sitemap, and robots.txt.
     3. Pre-deployment code check: verify 1 H1 per page, valid canonicals, valid JSON-LD schemas, all SVGs have explicit width/height, and `assets/css/styles.css` + `assets/js/main.js` exist.
     4. Deploy to Cloudflare Pages via Wrangler.
     5. Configure custom domains, proxied CNAMEs, Edge rewrite rules, and Email Routing.
     6. Add site to Google Search Console.
     7. Verify all live endpoints (including direct `styles.css` and `main.js` HTTP 200 checks) and output the live URLs immediately.
