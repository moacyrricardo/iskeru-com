# 001 — Custom bilingual 404 page

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
