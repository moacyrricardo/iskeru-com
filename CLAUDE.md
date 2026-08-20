# iskeru.com

Zero-dependency static-site generator: `build.py` (Python stdlib only) regenerates the whole site
into `dist/`. Bilingual — English at `/`, Portuguese under `/pt/`. Deployed to an nginx origin
behind Cloudflare via `deploy.sh` (rsync over SSH; needs `ISKERU_SSH` + `ISKERU_PATH`).

## Spec workflow
Tracker:        linear
Linear team:    BOL
Issue prefix:   iskeru:          # title tag marking iskeru issues within the BOL team — PROPOSED, adjust to taste
Branch prefix:  moacyrricardo/   # with a Linear issue: use Linear's generated branchName (e.g. moacyrricardo/bol-NN-slug); no issue: moacyrricardo/spec-NNN-slug
Specs dir:      specs/           # catalog index is specs/catalog.md (lowercase)

Notes: commits reference the Linear identifier (`BOL-NN Short description`) once issues exist;
specs 001–006 predate the tracker and use `spec-NNN` subjects. No `CONTRIBUTING.md` — commit/PR
division follows the global `~/.claude/CLAUDE.md` conventions.

## Build & test
Build: python3 build.py                          # regenerates the whole site into dist/
Test:  python3 -m unittest discover -s tests     # stdlib unittest; keep the zero-dependency policy

## Dev server
Start: python3 build.py && python3 -m http.server -d dist 8000   # build first, then serve dist/
Port:  8000
Ready: curl -sf http://localhost:8000/ returns 200
Auth:  none (public static site — no dev-login needed for evidence capture)

## API Modules
none    # static site — no compiled artifact is consumed as a library by another service
