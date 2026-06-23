# 002 — SEO positioning: intent-matched service pages

> Status: **doing** — branch `moacyrricardo/spec-002-seo-service-pages`.
> No Linear ticket for this work. PR open and unmerged (stays `doing` until merge).

## Context

The profile (`/about/`) is the commercial surface of iskeru.com, but it is written
as a single **personal bio** — name-first title, leadership/QuintoAndar narrative.
We want it to rank for commercial-intent queries the owner actually sells against:

- `fractional CTO` / `CTO for hire` / `fractional CTO for startups`
- `custom project development` / `custom software development` (with the AI-services angle)

Google ranks **pages against a query's intent**, not sites. One profile page
covering three distinct intents ranks weakly for all three. In particular
`custom project development` has **no page to rank** today — the copy sells
*leadership*, not *delivery*. The site also has **zero structured data** and **no
`og:image`**, both of which are low-effort wins the current `head()` lacks.

This spec covers only the **on-page** levers we control in `build.py`. Off-page
authority (backlinks, Google Business Profile, LinkedIn, directory listings) and
the long-tail-first ranking strategy are real but out of scope here — see Known
Gaps. iskeru.com is a new, low-authority domain, so head terms like `cto for hire`
are a months-long effort regardless of on-page quality; this work is the
necessary foundation, not a guarantee of head-term rankings.

## Decision

Split the single commercial surface into **intent-matched pages**, each with its
own title/H1/body/FAQ written around the literal queries, and add the missing
machine-readable SEO scaffolding site-wide.

1. **New service pages** (bilingual, EN at root + PT mirror, same `ROUTES`/`page()`
   machinery as every other page):
   - `/fractional-cto/` (PT `/pt/cto-fracional/`) — targets *fractional CTO / CTO
     for hire / advisory / engineering leadership on demand*.
   - `/custom-development/` (PT `/pt/desenvolvimento/`) — targets *custom software
     / project development*, foregrounding AI services.
   - `/about/` stays the **human profile** and links to both service pages.
2. **JSON-LD structured data** added in `head()`: `Person` (the owner) site-wide,
   plus `Service`/`ProfessionalService` on each service page.
3. **`og:image`** added to `head()` (currently only `twitter:card=summary`, no image).
4. **FAQ blocks** on each service page (real questions → long-tail + FAQ rich
   results).
5. **Internal linking** from home + nav to the service pages using the keyword as
   anchor text.

## Implementation

All edits are in `build.py` (stdlib generator) + `assets/styles.css` if new blocks
need styling. No framework, no new dependencies. `dist/` stays gitignored.

### Routes & nav (`build.py`)
- Add to `ROUTES`:
  - `"fractional_cto": {"en": "/fractional-cto/", "pt": "/pt/cto-fracional/"}`
  - `"custom_dev":     {"en": "/custom-development/", "pt": "/pt/desenvolvimento/"}`
- Add both to `NAV`/header (or a "Work with me" grouping) with keyword anchor text:
  EN "Fractional CTO" / "Custom development"; PT "CTO Fracional" / "Desenvolvimento".
- Add corresponding `<url>` entries to `render_sitemap()` with `hreflang` alternates
  (priority ~0.9, same as products). These pages **belong** in the sitemap (unlike
  the 404).

### Copy (`T`, both `en` and `pt`)
For each service page add a `*_title`, `*_desc` (meta description, ≤155 chars,
leads with the query), `*_h1`, lede, body sections, and an FAQ list of
`{q, a}` pairs. Suggested literal phrasing:
- Fractional CTO title: `Fractional CTO for Hire — Engineering Leadership On Demand | iskeru`
  H1: `Fractional CTO for hire`.
- Custom dev title: `Custom Software & Project Development (AI-focused) | iskeru`
  H1: `Custom project development`.
Reuse existing capabilities/experience/leadership data already in `build.py`
(the `200+ engineers`, QuintoAndar founding-team credibility) as proof on the
service pages — do not duplicate the whole bio.

### `head()` changes (`build.py`, ~line 443)
- Add `<meta property="og:image" content="{SITE}/assets/og-image.png" />` and the
  matching `twitter:image`; switch `twitter:card` to `summary_large_image`.
  Add the image asset to `assets/` and to the `STATIC` copy list.
- Inject a JSON-LD `<script type="application/ld+json">` block. Site-wide `Person`
  (name, jobTitle, sameAs LinkedIn/GitHub, knowsAbout). On service pages, also a
  `Service`/`ProfessionalService` node (`serviceType`, `provider` → the Person,
  `areaServed`). Drive it from a small `LD[key][lang]` builder so each page emits
  the right schema. Escape via `json.dumps` — do not hand-format.

### Render functions
- `render_fractional_cto()` and `render_custom_dev()` mirroring existing
  `render_about()` structure (hero + sections + FAQ), run through
  `page(lang, key, title, desc, body)` for both langs.
- Wire both into `main()` so they write `dist/fractional-cto/index.html`,
  `dist/pt/cto-fracional/index.html`, etc.
- FAQ blocks emit `FAQPage` JSON-LD too (eligible for FAQ rich snippets).

### Verification
- `python3 build.py` produces all four new HTML files + PT mirrors; both langs,
  correct canonical/hreflang, present in `sitemap.xml`.
- Validate JSON-LD (e.g. Google Rich Results test / `json.loads` round-trip in build).
- Titles/H1s contain the literal target phrases; meta descriptions ≤155 chars.
- `og:image` resolves; Twitter card is `summary_large_image`.
- Capture a gif/screenshot of each new page as PR evidence (per project convention),
  using the test agent / existing selenium venv.

## Known Gaps

- **Off-page is out of scope.** Backlinks, Google Business Profile, LinkedIn
  optimization, and directory listings (Clutch/GitHub for dev work) decide
  head-term rankings far more than on-page; tracked separately, not here.
- **Long-tail-first strategy** (`fractional AI CTO`, `fractional CTO for startups`,
  `fractional CTO Brazil`) is the realistic near-term win; this spec builds the
  pages that can capture it but does not include an ongoing content/keyword plan.
- **Alternative considered & rejected:** just optimizing the single `/about/` page
  (title/H1/schema) without splitting. Cheaper, but cannot rank for the distinct
  `custom project development` intent — no matching page. Rejected in favor of
  dedicated pages.
- **`og-image.png` asset** must be designed/produced; this spec assumes one
  1200×630 image. A per-page image variant is deferred.
- No analytics/rank-tracking setup is included.
