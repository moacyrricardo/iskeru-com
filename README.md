# iskeru.com

Bilingual static site for **iskeru** — products + personal profile. English at the
root, Portuguese (pt-BR) under `/pt/`.

Products (grouped by area on the products page):

- **Finance** — [boletim](https://boletim.iskeru.com), [minhabufunfa](https://minhabufunfa.iskeru.com), lineu-ai (soon)
- **Events** — [cevem](https://cevem.iskeru.com)
- **Buildings** — pacdoorman (soon)

## How it works

The site is **generated** from a single source by `build.py` (Python standard
library only — no npm, no framework). Output goes to `dist/`, which is **not
committed** (built at deploy time). Edit the content/data in `build.py` once and
both languages regenerate, so they never drift.

```bash
python3 build.py        # -> writes the full site into dist/
```

### Source (tracked — edit these)

```
build.py            Content data (CONTENT/PRODUCTS/…) + templates + the generator
assets/styles.css   Styles (no external dependencies)
assets/moacyr.jpg   Profile photo
favicon.svg         Icon
robots.txt          Indexing + sitemap pointer
deploy.sh           Build + ship to a remote box over SSH
```

### Generated (in `dist/`, gitignored — never edit by hand)

```
dist/index.html              EN home
dist/products/index.html     EN products
dist/about/index.html        EN profile
dist/pt/…                     PT mirror (/pt/, /pt/produtos/, /pt/sobre/)
dist/sitemap.xml             both languages, with hreflang alternates
dist/assets, favicon, robots  static assets copied in
```

URLs: EN at `/`, `/products/`, `/about/`; PT at `/pt/`, `/pt/produtos/`,
`/pt/sobre/`. Each page carries `hreflang` alternates and a header EN | PT switcher.

## Run locally

```bash
python3 build.py
python3 -m http.server -d dist 8000
# open http://localhost:8000
```

## Deploy

`deploy.sh` builds and ships `dist/` to a remote folder over SSH (rsync with
`--delete`, scp fallback). Target is parametrized by environment variables:

```bash
ISKERU_SSH=ubuntu@<host> ISKERU_PATH=/var/www/iskeru ./deploy.sh
```

`ISKERU_SSH` must be the box's real address or an `~/.ssh/config` host alias — not
the Cloudflare-proxied public domain.
