# 009 — fo-foca: point at the project site and its test builds

> Status: **doing**
> Branch: `moacyrricardo/spec-009-fofoca-project-site` · No Linear ticket.

## Context

Spec 008 put fo-foca on the products page ("Meetings") and published the "Building fo-foca"
post. At the time fo-foca ran only from source, so the card said "Pre-alpha — Linux, runs from
source" and its only call to action was "View on GitHub".

fo-foca now has a public project site, <https://moacyrricardo.github.io/fofoca/>, with a download
card for the newest GitHub release (AppImage, `.deb`, `fofoca-setup.sh`; currently
`v0.1.0-pr32`) and step-by-step Linux install instructions. Its badges still read
"Pre-alpha", "Linux x86-64", "Vulkan GPU · or CPU", "MIT", and the install section says
"Linux x86-64, test builds". The site links back to `https://iskeru.com/products/#fofoca` and
`/posts/building-fofoca/`.

## Decision

1. **Main call to action → the project site.** The fo-foca product's `cta_href` becomes
   `https://moacyrricardo.github.io/fofoca/`, labelled "Download & install" / "Baixar e instalar"
   with a download icon. This applies to the products page card and to the product box under the post.
2. **GitHub stays as a secondary link.** Product cards (and the post product box) get an optional
   secondary link: `cta2_href` + `cta2_icon` on the product, `cta2` text per language. Products
   without it render exactly as before. fo-foca uses it for "View on GitHub" / "Ver no GitHub".
3. **Status note** reflects the test builds: "Pre-alpha — Linux x86-64 test builds (AppImage, .deb)." /
   "Pré-alpha — builds de teste para Linux x86-64 (AppImage, .deb)."
4. **Features list** checked against the site's "What it does" and shipped Status items: keep live
   transcription, checked notes, speaker separation, calendar + replay and MIT; add tasks across
   meetings filtered by label, and "any Vulkan GPU (2 GB is enough) or CPU only". The description
   mentions the live "summary so far".
5. **Post (`posts/fofoca/`, both languages):** the post is dated 2026-11-20, so its story stays as
   written. Only the parts that are now wrong change: the "Packaging — AppImage" item gets a short
   dated note that test builds (AppImage and `.deb`) shipped, and "Try it" / "Testa aí" says
   test builds exist and links the project site for download and install, keeping the GitHub link.
   PT remains the author's text; the edits are minimal and mirrored in the EN translation.
6. **URLs unchanged.** The product anchor (`#fofoca`) and both post slugs stay, since the project
   site links to them.

## Implementation

- `build.py`: add a `download` icon; `product_article()` and `product_box()` render the optional
  `cta2` link after the main CTA; update the fo-foca entry in `PRODUCTS` (en + pt).
- `posts/fofoca/pt.md`, `posts/fofoca/en.md`: the two edits above.
- `tests/test_posts.py`: assert the card and the post product box link the project site and
  GitHub, the stale "runs from source" note is gone, and the post links the project site.

## Known Gaps

- The release version is not shown on iskeru.com on purpose: the project site looks up the newest
  build itself, so iskeru.com never goes stale on version numbers.
- Not deployed by this spec.
