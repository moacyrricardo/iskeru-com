# 003 — Landing performance: kill render-blocking CSS & Google Fonts (LCP)

> Status: **todo**
> Branch: _tbd_ · No Linear ticket.

## Context

A Google PageSpeed Insights run on `iskeru.com` flags the critical rendering path as the
main LCP drag. Everything below is authored in **one place** — `head()` in `build.py`
(lines 730–733), which every page renders through — so the fix is site-wide by construction.

**Insights findings:**

- **Render-blocking requests — est. saving ~1,970 ms.** Three resources block first paint:
  - `/assets/styles.css` (5.2 KiB transfer, ~170 ms) — `build.py:733`.
  - Google Fonts `https://fonts.googleapis.com/css2?family=Inter…&family=Space+Grotesk…` (1.6 KiB, ~780 ms) — `build.py:732`.
  - Cloudflare `…/cloudflare-static/email-decode.min.js` (1.2 KiB, ~500 ms) — **not** in our source; injected by Cloudflare Email Address Obfuscation.
- **Critical request chain — max latency 1,114 ms.** `iskeru.com` → `css2` (Google Fonts CSS) → `fonts.gstatic.com/*.woff2` (48 KiB + 23 KiB) → `/assets/styles.css`. The font files sit at the **end of a 3-hop cross-origin chain** and are the longest path.
- **Preconnect:** already present for `fonts.googleapis.com` and `fonts.gstatic.com` (`build.py:730–731`) — correct today, but becomes dead weight once fonts are self-hosted (see Decision).
- **Cache TTL — est. saving ~5 KiB.** `/assets/styles.css` at 7 days; Cloudflare-served `beacon.min.js` (1 day) and `email-decode.min.js` (~2 days) are Cloudflare-controlled.

**Precedent in-house:** `boletim.iskeru.com` (a sibling property) scores clean on exactly these
checks because its landing page **inlines all CSS in a `<style>` block and uses a system font
stack** — no external stylesheet, no web-font chain. This spec brings iskeru.com's `head()` to
the same shape where it makes sense, keeping the brand fonts.

## Decision

Remove all three render-blocking resources from the critical path, keeping the Inter / Space
Grotesk brand fonts by **self-hosting** them instead of chaining through Google Fonts.

1. **Self-host the web fonts.** Download the exact weights in use (Inter 400/500/600/700,
   Space Grotesk 500/600/700) as `woff2` into `assets/fonts/`. Add `@font-face` rules with
   `font-display: swap` to `assets/styles.css`. Delete the two `preconnect` hints and the
   `css2` `<link>` (`build.py:730–732`) — the html→googleapis→gstatic chain disappears.
   `preload` only the 1–2 faces actually used above the fold (hero H1 = Space Grotesk, body =
   Inter): `<link rel="preload" as="font" type="font/woff2" crossorigin href="…">`.

2. **Make the stylesheet non-blocking.** `assets/styles.css` is ~15 KB on disk (~5 KiB gzipped).
   Two acceptable options — pick per taste:
   - **(a) Inline it** into a `<style>` in `head()` (mirrors the boletim landing page). Simplest;
     removes the request entirely. Fonts still load via self-hosted `@font-face` in that inlined CSS.
   - **(b) Non-blocking link:** `<link rel="preload" as="style" href="/assets/styles.css"
     onload="this.rel='stylesheet'">` + `<noscript>` fallback, with critical above-the-fold CSS
     inlined. More machinery; only worth it if the CSS grows well past ~15 KB.

   Recommendation: **(a)** at current CSS size — one `<style>` block, zero render-blocking requests.

3. **Cloudflare Email Address Obfuscation** (source of `email-decode.min.js`). Turn off
   **Scrape Shield → Email Address Obfuscation** in the Cloudflare dashboard (it can't be
   deferred from our source — Cloudflare injects the blocking script whenever it rewrites a
   `mailto:`). If we want to keep some scraping protection, replace plain `mailto:` links with a
   non-obfuscatable form (e.g. a contact route) so Cloudflare finds nothing to rewrite.

4. **Cache TTL.** Serve `/assets/*` with a long-lived, immutable policy
   (`Cache-Control: public, max-age=31536000, immutable`) via a Cloudflare cache rule and/or the
   response headers set in `deploy.sh`. Because our asset URLs are unversioned, pair long TTL with
   a cache-busting query/hash on the `styles.css` / font references, or purge on deploy. The
   Cloudflare-served `beacon.min.js` / `email-decode.min.js` TTLs are not ours to set (item 3
   removes the latter).

## Implementation

- **`build.py` `head()` (702–737):** drop lines 730–732; replace line 733 per Decision #2
  (inline `<style>…</style>`, or preload-swap link). Add font `preload` hints.
- **`assets/styles.css`:** prepend `@font-face` blocks (self-hosted `woff2`, `font-display: swap`).
  `--font-sans` (Inter) / `--font-display` (Space Grotesk) variables already exist (defined lines 26–27; used at 37, 50).
- **`assets/fonts/`:** new — the subsetted `woff2` files.
- **`deploy.sh` / Cloudflare:** cache-control for `/assets/*`; disable Email Address Obfuscation.

## Known Gaps

- **Cloudflare-served assets** (`beacon.min.js`, and `email-decode.min.js` until Email Obfuscation
  is off) have Cloudflare-controlled TTLs — outside repo control.
- **Font subsetting:** Latin-only subsets keep the `woff2` payload small; if non-Latin glyphs are
  ever needed, revisit the subset.
- **Unversioned asset URLs** vs. long immutable TTL — needs a hashing/purge story (Decision #4).

## Verification

Re-run PageSpeed Insights (and a WebPageTest filmstrip) on `iskeru.com` after deploy; expect the
render-blocking group to clear (styles.css + Google Fonts gone) and the critical-path max latency
to drop from ~1,114 ms toward the self-hosted-font first-byte. Confirm the visible font is still
Inter / Space Grotesk (no FOUT beyond the `swap` flash). Save the before/after under
`specs/evidence/`.
