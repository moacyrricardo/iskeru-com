# iskeru.com

Bilingual static site for **iskeru** — presents the company, its products, and the
founder's consulting/advisory. English at the root, Portuguese (pt-BR) under `/pt/`.

Products (grouped by area on the single products page):

- **Finance** — [boletim](https://boletim.iskeru.com) (financial automation),
  [minhabufunfa](https://minhabufunfa.iskeru.com) (personal finance) and
  lineu-ai (AI automation — coming soon at lineu-ai.iskeru.com)
- **Events** — [cevem](https://cevem.iskeru.com) (invitations & RSVP)
- **Buildings** — pacdoorman (package management over WhatsApp — coming soon)

## How it works

The HTML is **generated** from a single source by `build.py` (Python standard
library only — no npm, no framework). Edit the content/data in `build.py` once and
both languages are regenerated, so they never drift.

```bash
python3 build.py        # regenerates all pages + sitemap.xml
```

### Source (edit these)

```
build.py            Content data (CONTENT/PRODUCTS) + templates + the generator
assets/styles.css   Styles (no external dependencies)
favicon.svg         Icon
robots.txt          Indexing + sitemap pointer
```

### Generated output (do not edit by hand — re-run build.py)

```
index.html               EN  home
products/index.html      EN  products (Finance / Events / Buildings)
about/index.html         EN  founder + consulting
pt/index.html            PT  home
pt/produtos/index.html   PT  products
pt/sobre/index.html      PT  consultoria / advisory
sitemap.xml              both languages, with hreflang alternates
```

URLs: EN at `/`, `/products/`, `/about/`; PT at `/pt/`, `/pt/produtos/`,
`/pt/sobre/`. Each page carries `hreflang` alternates and a header language
switcher (EN | PT).

## Run locally

```bash
python3 build.py
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy

Any static host (nginx, Cloudflare Pages, S3, etc.). Run `python3 build.py`, then
serve the repository root. Make sure `robots.txt` and `sitemap.xml` are reachable at
`https://iskeru.com/robots.txt` and `https://iskeru.com/sitemap.xml`.

> **Sitemap note:** it lists only `iskeru.com` pages. The `cevem`, `boletim` and
> `minhabufunfa` subdomains are their own hosts and should ship their own
> `sitemap.xml` / `robots.txt`.
