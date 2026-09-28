# Master Blueprint: Core Website Development & Technical SEO

This document serves as the persistent master specification and implementation standard for building fast, high-converting, and SEO-optimized local business websites.

---

## 0. Mandatory Pre-Creation Intake Questionnaire

Before generating any site code or pages, collect the following required parameters:
1. **Website / Business Name**: Official registered name and brand DBA.
2. **Website Address**:
   - **Physical Location / Service Area**: Street address, suite, city, state, zip (or service radius).
   - **Domain URL**: Canonical domain (e.g. `https://www.example.com`).
3. **Website Phone Number**: Local or tracking number used for `tel:` links and GMB NAP consistency.
4. **Business Category**: Primary Google Business Profile (GBP) category and industry niche.
5. **Operating Hours**: Regular weekly schedule and emergency / weekend availability.
6. **Target Keywords**: Primary geo-targeted keywords and core service terms.
7. **Competitor URLs**: Top 2–3 local or regional competitors for SERP benchmarking.

---

## 1. Core Website Architecture

### 1.1 Performance-First Directory Structure
```text
website-root/
├── assets/
│   ├── css/
│   │   ├── critical.css       # Inlined in <head> for instant FCP (< 14KB)
│   │   └── styles.css         # Deferred main stylesheet
│   ├── js/
│   │   ├── main.js            # Core interactive logic (deferred)
│   │   └── analytics.js       # GA4/GTM conversion event tracking
│   ├── images/                # Next-gen formats (.webp, .avif)
│   │   ├── hero/
│   │   ├── team/
│   │   └── trust-badges/
│   └── fonts/                 # Self-hosted WOFF2 font files
├── components/
│   ├── header.html            # Semantic header + desktop phone CTA
│   ├── footer.html            # NAP consistency + schema + quick links
│   └── call-bar.html          # Mobile sticky bottom conversion bar
├── pages/
│   ├── index.html             # Homepage
│   ├── about-us.html          # High-trust story + proof matrix
│   ├── services/              # Core siloed service pages
│   ├── locations/             # Geo-targeted service area pages
│   └── contact.html           # Full NAP, form, and Google Maps embed
└── sitemap.xml & robots.txt
```

### 1.2 Core Web Vitals Optimization Rules
- **Largest Contentful Paint (LCP < 2.5s)**:
  - Hero image preloaded with `fetchpriority="high"`.
  - Avoid rendering blocking JavaScript in `<head>`.
  - Inline critical CSS inside `<style>` in `<head>`.
- **Interaction to Next Paint (INP < 200ms)**:
  - Break long JavaScript tasks into smaller chunks.
  - Zero heavy third-party scripts execution during main-thread page load.
- **Cumulative Layout Shift (CLS < 0.1)**:
  - Every `<img>`, `<video>`, and `<iframe>` must have explicit `width` and `height` attributes or CSS `aspect-ratio`.
  - Reserve space for dynamic elements and banners.

---

## 2. Essential Feature: High-Converting "Click-to-Call" Button

- **Mobile Viewport**: Persistent bottom-anchored sticky bar (`position: fixed; bottom: 0;`). Minimum touch target height: `52px` (exceeds WCAG 48px standard).
- **Desktop Viewport**: Prominently placed in the upper-right header with operating status (`Available Now` dot) and company phone number.
- **Tracking**: Built-in Google Analytics 4 (`dataLayer.push`) and Google Ads conversion firing.

*Template File*: [`../templates/click-to-call.html`](file:///c:/Users/ammar/OneDrive/Desktop/GMB/templates/click-to-call.html)

---

## 3. Core Page Strategy: High-Trust "About Us" Page

### 3.1 UX Flow & Layout Blueprint
1. **Hero Section**: Geo-specific value proposition + founder/team in action + primary license badges.
2. **Quantified Proof Matrix**: 4 key stats (Years in Business, Completed Projects, Review Rating, Warranties).
3. **The Origin / Mission Story**: Focuses on why the business was founded, solving customer pain points, and commitment against subcontractor shortcuts.
4. **Meet the Leadership & Team**: Authentic names, photos, credentials, and bio blurbs (direct Google E-E-A-T signal).
5. **Accreditations & Guarantees**: BBB badge, local Chamber of Commerce, manufacturer certifications, satisfaction guarantee.
6. **Customer Proof Carousel**: Real client testimonials tied to specific neighborhoods or cities.
7. **Direct Conversion CTA**: Dual options (Immediate Call + Free Online Inspection/Estimate).

*Template File*: [`../templates/about-us.html`](file:///c:/Users/ammar/OneDrive/Desktop/GMB/templates/about-us.html)

---

## 4. Technical & On-Page SEO (Day 1 Implementation)

### 4.1 Heading Tag Hierarchy
- **`<h1>`**: Exactly one per page. Must contain: `[Primary Service Keyword] in [Target City/Geo] | [Brand Hook]`.
- **`<h2>`**: Major content sections (e.g., Core Services, Local Customer Benefits, Case Studies, FAQs).
- **`<h3>`**: Sub-points or individual services under an `<h2>` section.
- *Strict Rule*: Never use heading tags for visual styling; use utility classes (e.g., `.text-xl`, `.font-bold`) to change size while preserving semantic hierarchy.

### 4.2 Semantic HTML Landmarks
- `<header role="banner">`
- `<nav aria-label="Main Navigation">`
- `<main role="main">`
- `<article>` for self-contained items (team cards, review cards, blog posts).
- `<section aria-labelledby="...">` for distinct topical sections.
- `<address>` for physical location and contact phone.
- `<footer role="contentinfo">`

### 4.3 Image Optimization Standards
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" 
       alt="Master roofer installing architectural shingles in Brooklyn NY" 
       width="800" 
       height="600" 
       loading="lazy" 
       decoding="async">
</picture>
```

### 4.4 Meta Tags & Social Graph
*Template File*: [`meta-tags-boilerplate.html`](file:///c:/Users/ammar/OneDrive/Desktop/GMB/seo/meta-tags-boilerplate.html)

### 4.5 Production-Ready JSON-LD Schema
*Schema File*: [`schema-local-business.json`](file:///c:/Users/ammar/OneDrive/Desktop/GMB/seo/schema-local-business.json)
