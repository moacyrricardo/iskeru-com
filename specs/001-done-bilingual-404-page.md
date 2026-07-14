# 001 — Custom bilingual 404 page

> Status: **done** — branch `moacyrricardo/spec-001-bilingual-404-page`.
> No Linear ticket for this work. Shipped via PR #1, merged to `main` 2026-06-22.
> **Operational follow-up completed 2026-07-14:** the origin nginx `error_page` +
> `internal` wiring is applied and verified live — see Verification status.

## Context

iskeru.com is a generated static site (`build.py`, stdlib only) deployed to an
nginx origin behind Cloudflare. There is currently **no custom 404 page** — an
unknown URL falls back to nginx's bare default error page, which is unstyled,
unbranded, and offers the visitor no way back into the site.

The site is bilingual: English at the root (`/`, `/products/`, `/about/`) and
Portuguese under `/pt/` (`/pt/`, `/pt/produtos/`, `/pt/sobre/`). A 404 can be
served at any path depth, so it must not assume its own location.

## Decision

Generate a **single bilingual `dist/404.html`** from the existing page template
and serve it via nginx's `error_page` directive.

- One file, both languages shown (EN section + PT section stacked, or EN with a
  visible "Português" toggle), so a single static file works for any path
  regardless of whether the visitor was on an EN or PT URL.
- Reuse the existing header/footer/`PAGE` template so it is styled and carries
  the EN | PT switcher and nav, giving the visitor an obvious way back.
- All asset and navigation links must be **absolute** (`/`, `/assets/...`,
  `/products/`) since the page is served at arbitrary depths. The site already
  uses absolute links, so no template change is needed for this.

## Implementation

1. **`build.py`**
   - Add a 404 content block to the existing `CONTENT`/translation structures:
     a heading, a short "page not found" message, and a couple of links back
     (home, products) — in both `en` and `pt`.
   - Add a generator step that renders the 404 body through the shared `PAGE`
     template (same `<head>`, favicon, header switcher, footer) and writes it to
     `dist/404.html`. It is a single root-level file — no `/pt/404.html`.
   - The 404 is **not** added to `sitemap.xml` and **not** linked from nav; it is
     reachable only via nginx error routing.
   - Confirm the generated HTML uses only absolute paths for assets/links.

2. **nginx (origin box)**
   - Add to the server block:
     ```nginx
     error_page 404 /404.html;
     location = /404.html { internal; }
     ```
   - `internal` prevents the page from being requested directly with a 200.
   - This config change lives on the origin, not in the repo; note it in the
     deploy notes / README so it survives a server rebuild.

3. **Verification**
   - `python3 build.py` produces `dist/404.html`.
   - Locally: `python3 -m http.server -d dist 8000` then request a bogus path and
     confirm the styled page renders with working nav/assets.
   - After deploy: `curl -I https://iskeru.com/does-not-exist` returns
     `HTTP/2 404` with the custom page body, and assets load (absolute paths).

## Known Gaps

- **Single page vs. per-language pages.** A more "correct" approach would serve a
  Portuguese 404 for `/pt/*` paths via a second `dist/pt/404.html` plus an nginx
  `location /pt/ { error_page 404 /pt/404.html; }` block. This is deliberately
  deferred — the single bilingual page is simpler, needs no path-aware routing,
  and covers both audiences. Revisit only if analytics show meaningful PT 404
  traffic that warrants language-specific handling.
- **Cloudflare.** Assumes Cloudflare passes the origin's 404 through. If Cloudflare
  is ever switched to Pages or a custom error page, this directive becomes moot —
  out of scope here.
- No `apple-touch-icon` / `.ico` fallback work — unrelated to 404s.

## Implementation Notes

Implemented exactly as decided; the bilingual content is **two hero sections
stacked** (EN then PT) inside one `<main>`, each marked with `lang="..."`.

How the implementation maps to the existing `build.py` idioms:

- **`ROUTES`** gained a `"notfound"` entry (`/404.html` for both `en` and `pt`).
  This lets the page reuse the shared `head()`/`header()` template unchanged: the
  canonical URL, the `hreflang` alternates and the EN | PT switcher all resolve
  through `ROUTES["notfound"][lang]` like every other page. Because the 404 is a
  single file, both languages point the switcher at the same `/404.html`.
- **`T`** gained an `nf_*` block (title, desc, eyebrow, h1, lede, two back-link
  labels) for both `en` and `pt`, following the existing per-page copy convention.
- **`render_notfound()`** mirrors `render_home`/`render_products`/`render_about`
  but takes no `lang` (it renders both): it stacks `notfound_block(lang)` for each
  language and runs the result through `page("en", "notfound", …)`. The page chrome
  (html lang, switcher active state, footer) is rendered in EN as the root default;
  the body carries both languages.
- **`main()`** writes `dist/404.html` directly (single root file, no lang loop, no
  `/pt/` variant) — handled alongside the `sitemap.xml` write rather than through
  the `RENDERERS`/`out_path()` per-language loop.
- **`render_sitemap()`** explicitly `continue`s past the `notfound` key so the 404
  never appears in `sitemap.xml`. It is also not linked from nav.
- **All links are absolute** — confirmed by construction: `ROUTES` values, the
  favicon (`/favicon.svg`) and stylesheet (`/assets/styles.css`) in `head()` are
  all root-absolute, so the page is depth-independent.

### Deviations / notes

- **Single `render_notfound()` (no `lang` parameter).** Unlike the other
  renderers it does not loop per language at the call site — it is the one page
  that is intentionally bilingual-in-one-file, so the lang-loop lives *inside* it.
- **nginx config** (`error_page 404 /404.html; location = /404.html { internal; }`)
  documented in `README.md` under a new "Custom 404" section; it lives on the
  origin box, not in the repo.
### Verification status

The **build/repo side is done and deployed:**

- `python3 build.py` produces `dist/404.html` (single root file, excluded from
  `sitemap.xml`).
- The page is live on the origin: `GET https://iskeru.com/404.html` → **200**,
  styled, with both `lang="en"` and `lang="pt-BR"` sections and absolute asset
  links (`/assets/styles.css`) — confirmed 2026-06-25.

**Operational step (origin box, not the repo) — completed 2026-07-14.** The nginx
server block for `iskeru.com` now carries the wiring the spec always called out
(documented in `README.md` → "Custom 404"):

```nginx
error_page 404 /404.html;
location = /404.html { internal; }
```

Verified live 2026-07-14: `curl https://iskeru.com/<bogus>` returns `404` with the
**custom** styled body ("Page not found" / iskeru markup, no longer the default
`nginx/1.24.0` page), and `GET /404.html` now returns `404` rather than being
directly fetchable with `200` — the `internal` clause is in effect. The spec is
fully delivered (code **and** ops).

> Historical: as of 2026-06-25 this step was still outstanding — the page was live
> at `/404.html` (200) but nginx served its default body on unknown URLs.
