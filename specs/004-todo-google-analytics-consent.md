# 004 — Google Analytics (GA4) with Consent Mode v2

> Status: **todo**
> Branch: _tbd_ · No Linear ticket.

## Context

We want to measure traffic and on-site behaviour for `iskeru.com` — page views, sessions,
engagement, scroll depth, outbound clicks, downloads — to see which products and service pages
draw interest and how visitors move through the bilingual site.

**Product.** Google Analytics 4 (GA4) is the current and only Google Analytics product in 2026
(Universal Analytics was sunset July 2023 and its data deleted July 2024; no successor). Tagging
is the standard `gtag.js` snippet keyed by a **Measurement ID** in `G-XXXXXXXXXX` form, obtained
from Admin → Data Streams → (web stream) at analytics.google.com. The Measurement ID is a
**public, client-side value** — it appears in every page's source by design, so hardcoding it in
`build.py` is correct and it needs no secret handling.

**Single injection point.** Every page renders through `head()` (`build.py:731–766`) in both
languages, so — exactly like spec 003 — one edit there is site-wide by construction. No nginx or
`deploy.sh` change is required; the generated HTML in `dist/` carries the tag.

**Audience → consent required.** The site is bilingual EN / PT‑BR and serves EU/EEA and Brazil
visitors. GA4 anonymises IPs automatically (non-configurable since 2022 — no `anonymize_ip`
needed) but **still sets non-essential cookies** (`_ga`, `_ga_*`). Under GDPR/ePrivacy (and
Brazil's LGPD) those cookies may only be set **after** the visitor consents. We therefore ship
GA4 behind **Google Consent Mode v2**, denied by default, gated by a lightweight cookie banner —
not a bare snippet. (Decision confirmed with the owner: Consent Mode v2 + banner, over a
no-banner minimal install or a cookieless alternative.)

**What GA4 gives us out of the box.** With Enhanced Measurement (on by default on the web stream)
the base tag alone reports `page_view`, `scroll` (90% depth), outbound `click`, `file_download`,
`view_search_results`, video and basic `form_start`/`form_submit` — no custom events needed for
the "traffic + behaviour" goal. Custom `gtag('event', …)` calls are out of scope for this spec.

**Interaction with spec 003.** Spec 003 removes the Google Fonts `preconnect`/`css2` chain from
`head()` to clear render-blocking. GA adds one `async` request to
`www.googletagmanager.com` — non-blocking (the `async` attribute keeps it off the critical path),
so it does not reintroduce the LCP problem 003 fixes. If 003 lands first, add a single
`<link rel="preconnect" href="https://www.googletagmanager.com">`; the two specs are otherwise
independent and can land in either order.

## Decision

Add GA4 via `gtag.js` in `head()`, **gated behind Consent Mode v2 (analytics denied by default)**
and a minimal bilingual cookie-consent banner. Concretely:

1. **Config constant.** Add `GA_MEASUREMENT_ID = "G-XXXXXXXXXX"` near the other site constants in
   `build.py` (owner replaces the placeholder with the real stream ID). If it is left empty/None,
   `head()` emits **no** analytics markup at all — so the build stays clean until the ID exists.

2. **Head order (strict).** Inside `head()`, immediately after `<head>` and **before** any other
   resource, emit in this order:
   1. **Consent Mode defaults — denied.** An inline script that defines `dataLayer`/`gtag` and
      calls `gtag('consent', 'default', { ad_storage:'denied', ad_user_data:'denied',
      ad_personalization:'denied', analytics_storage:'denied', wait_for_update: 500 })`. This must
      run *before* the tag loads, or Consent Mode does nothing.
   2. **The gtag.js tag.** `<script async src="…/gtag/js?id=<ID>">` then an inline
      `gtag('js', new Date()); gtag('config', '<ID>')`. The `<ID>` placeholder is filled from the
      constant in **both** places (a common pitfall is replacing only one).

3. **Host gate (don't track ourselves / dev).** Wrap the `config` call so it only runs on the
   production host: `if (location.hostname === 'iskeru.com') { gtag('config', '<ID>'); }`.
   Localhost and preview builds then load nothing meaningful, keeping dev traffic out of GA
   without a separate build flag. (Also define internal traffic by IP in GA4 Admin as belt-and-
   suspenders — an out-of-repo step.)

4. **Consent banner (bilingual, no dependency).** A small, self-contained banner appended near the
   end of `<body>` (in `footer()` or a new `consent_banner(lang)` helper), styled to match the
   site, with **Accept** and **Decline** actions:
   - On **Accept**: `gtag('consent', 'update', { analytics_storage:'granted' })` (ad_* stay
     denied — we run analytics only, no ads), persist the choice (e.g. `localStorage`
     `iskeru_consent = 'granted'`), hide the banner.
   - On **Decline**: persist `'denied'`, hide the banner; nothing is granted.
   - On load: if a stored choice exists, apply it (replay `consent update` on `granted`) and don't
     show the banner. No banner is shown once a choice is made.
   - All strings live in the `T[lang]` dict (`build.py:382`, EN + PT‑BR) alongside `skip`/
     `footer_note`, so the banner is translated like the rest of the site.

5. **Privacy policy link.** The banner and footer link to a **privacy/cookie policy** page that
   discloses GA4 use, the cookies set, and how to withdraw consent. The site currently has **no
   such page** — this spec adds a minimal bilingual one (new route `privacy`:
   `/privacy/` · `/pt/privacidade/`, following the existing `ROUTES`/`render_*` pattern), since a
   consent banner pointing at a non-existent policy is not defensible. Keep it minimal and factual;
   a fuller legal review can follow separately.

## Implementation

- **`build.py` constants:** add `GA_MEASUREMENT_ID = "G-XXXXXXXXXX"` beside `SITE`/`EMAIL`
  (`build.py:20–24`).
- **`build.py` `head()` (731–766):** after `<head>` (line 738), inject the consent-default +
  gtag.js block (Decision #2/#3), guarded by `if GA_MEASUREMENT_ID:` so an empty ID emits nothing.
  If spec 003 is already merged, add the `googletagmanager.com` preconnect here too.
- **`build.py` `T` dict (382 / 495):** add banner strings per language — headline, body sentence,
  **Accept** / **Decline** labels, and the privacy-link text.
- **`build.py` banner:** a `consent_banner(lang)` helper emitted from `page()`/`footer()` so it
  appears on every page; inline `<style>`/`<script>` (stdlib-only, zero-dependency policy — no CMP
  library). The banner script and the `gtag` glue can share the existing footer `<script>`
  (`build.py:819–830`).
- **`build.py` privacy page:** new `ROUTES["privacy"]` entry, a `render_privacy(lang)` function
  mirroring `render_about` (`build.py:1040`), wired into the page loop and `render_sitemap()`
  (`build.py:1309`); add nav/footer links if desired (optional — a footer link is enough).
- **`tests/` (new, stdlib `unittest` like `test_seo_service_pages.py`):** build the site into a
  temp dir and assert:
  - when `GA_MEASUREMENT_ID` is set, **every** `dist/**/*.html` contains the ID and the
    `consent 'default'` call precedes the `gtag/js` script (order invariant);
  - the `consent 'default'` block sets `analytics_storage:'denied'`;
  - when `GA_MEASUREMENT_ID` is empty, **no** page contains `googletagmanager.com` (clean-build
    invariant);
  - the privacy route exists in both languages and is in `sitemap.xml`.
- **Out-of-repo (owner):** create the GA4 property + web stream to mint the real `G-…` ID; leave
  Enhanced Measurement on; set data retention (default 2 months; 14 available); define internal
  traffic by IP in Admin. Verify via the Realtime report post-deploy.

## Known Gaps

- **No custom events / conversions.** Only Enhanced Measurement's built-in events ship. CTA-click
  or contact-conversion tracking, if wanted, is a follow-up spec.
- **Consent banner is minimal, not a certified CMP.** Accept/Decline only (no granular
  per-category toggles, no IAB TCF string). Adequate for a small first-party analytics-only site;
  revisit if ad/marketing tags are ever added.
- **Privacy policy is a minimal disclosure**, not a lawyer-reviewed document — sufficient to back
  the banner; a formal review can follow.
- **Measurement ID is public** and anyone can post junk hits to it — inherent to client-side
  analytics; not mitigated here.
- **`ad_*` signals stay denied** even on Accept (analytics-only). If Google Ads/remarketing is
  ever added, the banner copy and the granted signals must be revisited for Consent Mode v2
  compliance.

## Verification

- `python3 -m unittest discover -s tests` passes (new consent/ID invariants above).
- Build locally, open a page: confirm the banner shows on first visit, no `_ga` cookie is set
  before **Accept**, and `_ga`/`_ga_*` appear only after (DevTools → Application → Cookies).
- Deploy; on `iskeru.com` accept the banner and confirm the visit lands in GA4 **Realtime**
  (data can take up to ~30 min for standard reports). Confirm a `localhost` build sends nothing
  (host gate). Save a before/after (Realtime screenshot + a cookie-timeline note) under
  `specs/evidence/`.
