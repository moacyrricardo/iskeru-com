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
| 004 | Google Analytics (GA4) with Consent Mode v2 | ⚪ todo | Add `gtag.js` in `head()` behind Consent Mode v2 (analytics denied by default) + a minimal bilingual cookie banner; host-gated to `iskeru.com`. Adds a minimal privacy page (`/privacy/`, `/pt/privacidade/`). Owner supplies the `G-…` Measurement ID. No branch yet. |

## Notes

- **003 and 004 are the open work.** 003 touches `build.py` `head()` (self-host fonts,
  inline/non-block CSS) plus two out-of-repo steps — a Cloudflare dashboard change
  (disable Email Address Obfuscation) and a `/assets/*` cache-control policy — that
  can't be fully verified from the repo alone. Note the origin already serves
  `/assets/` at `expires 7d` (modest, non-fingerprinted); spec-003 §4 revisits this.
- **004** touches the same `head()` choke point (GA4 tag + Consent Mode defaults) plus the
  `T` dict and a new `render_privacy` page; the only out-of-repo steps are creating the GA4
  property/stream to mint the `G-…` ID and setting internal-traffic/retention in GA4 Admin.
  004's `googletagmanager.com` request is `async` (off the critical path), so it does not
  reintroduce the render-blocking 003 fixes — the two can land in either order.
