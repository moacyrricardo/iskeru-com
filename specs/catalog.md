# Spec catalog

The architectural decision record for **iskeru.com** — the generated static site
(`build.py`, Python stdlib only; bilingual EN root + PT under `/pt/`; deployed to an
nginx origin behind Cloudflare via [`deploy.sh`](../deploy.sh)). Each piece of work
lands as a numbered spec (`NNN-status-slug.md`, status `todo`/`doing`/`done` by file
rename). There is **no Linear ticket** for this repo — specs carry no issue id and
commits use `spec-NNN` subjects.

Filename status is the source of truth once merged to `main`; the **Status** column
below also reflects in-flight work (a spec reads `todo` on `main` until its PR merges
and renames it). Before/after evidence lives under [`evidence/`](./evidence).

## Specs

| # | Spec | Status | Notes |
|---|------|--------|-------|
| 001 | Custom bilingual 404 page | ✅ done | PR #1 → `main` 2026-06-22 (finish PR #6). Origin nginx `error_page`/`internal` wiring **applied & verified live 2026-07-14** (bogus URL serves the custom page; `/404.html` no longer directly fetchable). |
| 002 | SEO positioning: intent-matched service pages | ✅ done | PR #2 → `main` 2026-06-23 (merge `7851d37`, finish PR #3). Fractional-CTO + custom-development pages, JSON-LD structured data, `og:image`. |
| 003 | Landing performance: kill render-blocking CSS & Google Fonts (LCP) | ⚪ todo | Self-host Inter/Space Grotesk fonts + inline CSS to clear PageSpeed render-blocking (~1,970 ms) and the 3-hop font critical chain. Also Cloudflare Email-Obfuscation removal + `/assets/*` cache TTL. No branch yet. |
| 004 | Google Analytics (GA4) with Consent Mode v2 | ✅ done | PR #10 → `main` 2026-08-20 (merge `14fa2f0`). `gtag.js` in `head()` behind Consent Mode v2 (analytics denied by default) + bilingual cookie banner (dark, high-contrast — fixed post-review); host-gated to `iskeru.com`; minimal privacy page (`/privacy/`, `/pt/privacidade/`). Measurement ID `G-H4S91E1LWD`. Deployed; Realtime confirmed receiving. GTM preconnect deferred until 003. |
| 005 | GA4 interaction events: profile/repo/contact funnel + engagement | ⚪ todo | Host+path-classified `profile_click` / `repo_click` / `contact_click` events via one standalone delegated listener; broadens 004's host-gate to `www` (allowlist); updates privacy page to disclose interaction tracking. Funnel/Key-events/dimensions in GA4 console; search queries deferred to spec 006. **Revised after red-team** (consent-bias ceiling, github over-match, ES5-safety, stale citations). No branch yet. |
| 006 | Search Console: sitemap + GA4 link (already verified) | ⚪ todo · owner-exec | **Red-team + live DNS re-scoped this:** iskeru.com is **already verified** (a `google-site-verification` TXT exists; owner confirms). So 006 collapses to submit `sitemap.xml` + link GSC↔GA4 + confirm `www`→apex canonicalisation (www serves 200, not NXDOMAIN). No default-path code; **not autopilot-buildable**. No branch yet. |

## Notes

- **003 and 005 are the open work** (004 shipped & deployed). 003 touches `build.py` `head()`
  (self-host fonts, inline/non-block CSS) plus two out-of-repo steps — a Cloudflare dashboard
  change (disable Email Address Obfuscation) and a `/assets/*` cache-control policy — that
  can't be fully verified from the repo alone. Note the origin already serves `/assets/` at
  `expires 7d` (modest, non-fingerprinted); spec-003 §4 revisits this.
- **005** builds on 004: adds explicit interaction events (`social_click`, `contact_click`) via
  one delegated footer listener + broadens 004's host-gate to `www`. Most of its value (funnel
  exploration, Key events, custom dimensions) is GA4-console config, out-of-repo. Engagement-time
  reporting needs no code (Enhanced Measurement already collects it). Depends on 004 (merged);
  independent of 003.
- **006** Search Console — the search-query side of analytics (ask surfaced during 005). Re-scoped
  after a red-team + live DNS check found iskeru.com **already verified** (existing TXT, owner's
  account): now just submit the existing `sitemap.xml`, link GSC↔GA4, and confirm `www`→apex
  canonicalisation. Owner-executed, no default-path code — don't run it through the ship workflow.
