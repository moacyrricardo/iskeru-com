# 008 — Posts: bilingual articles with Claude-translated counterparts

> Status: **doing**
> Branch: `moacyrricardo/spec-008-bilingual-posts` · No Linear ticket.

## Context

The author wants to publish articles on iskeru.com, linked from short LinkedIn posts. The first one
is about building fo-foca (a local-only, pt-BR-first meeting-notes app). A clickable mock and an
editing pass happened on 2026-11-20; the decisions below come from that review. The articles also
serve the AI-visibility work (2026-11-12 call): original, technical content with real numbers,
published as HTML at URLs that never change.

## Decision

1. **Posts section** at `/posts/` (EN) and `/pt/posts/` (PT), labelled **"Posts"** in both
   languages, linked from the header and footer between "Custom development"/"Desenvolvimento"
   and "Profile"/"Perfil".
2. **Every post exists in both languages.** The author writes in one; Claude translates the other.
   The translation is labelled: a "Translated by Claude" / "Traduzido pelo Claude" badge in the
   list, and a banner on the post linking to the original. Each language has its own slug
   (`/pt/posts/construindo-fofoca/` ↔ `/posts/building-fofoca/`); the pair is linked with
   `hreflang` like every other page, and the EN/PT switch goes to the counterpart.
3. **Source format:** one folder per post, `posts/<id>/` with `pt.md`, `en.md` and `media/`.
   Markdown with front matter, rendered by `build.py` with a small stdlib renderer (zero-dependency
   policy unchanged).
4. **Media:** `posts/<id>/media/*` is published at `/assets/posts/<id>/`. A line
   `*(embed: … <file>.html)*` becomes an iframe of that media file; `![alt](file)` becomes an image
   (used for the app demo GIF, placed under the TL;DR).
5. **First post, fo-foca:** PT text is the author's (verbatim), with two links added:
   `/prototype` → the prototype skill guide, "catálogo numerado" → the spec-workflow guide. EN is
   Claude's translation. The benchmark report is published as a cleaned copy: no local paths,
   no session names, "your recording" → "the author's recording".
6. **fo-foca on the products page** in a new area, "Meetings" / "Reuniões" (it isn't
   infrastructure), status open source, linking to GitHub and to the post.

## Implementation

### `build.py`
- `POSTS`: loaded from `posts/*/` at build time. Front matter keys: `title`, `slug`, `lang`,
  `date`, `author`, `tags`, `reading_time`, `summary`, `cover` (media file), `product` (product
  slug), `translated_by` (present on the translation only).
- Routes: `posts` → `{"en": "/posts/", "pt": "/pt/posts/"}` and one `post:<id>` route per post,
  added to `ROUTES` so `head()`, `header()` (lang switch) and `render_sitemap()` pick them up.
- `render_markdown(src, media_base)`: H2–H4, paragraphs, bold, italics (`*x*` and `<i>x</i>`),
  inline code, links `[t](url)`, bare `github.com/...` links, lists with continuation lines,
  blockquotes, tables (wrapped in an `overflow-x` container), images, embed lines. All text HTML-escaped.
- Post page: cover image, "Posts" eyebrow, H1, author · date · reading time, translation banner,
  tags, prose, product card (from `product`), "All posts" link.
- Posts index: newest first; date, reading time, translation badge, title, summary, tags.
- JSON-LD on a post: `BlogPosting` with `headline`, `description`, `datePublished`, `inLanguage`,
  `url`, `image`, `author: {"@id": PERSON_ID}`, `keywords`; the translation adds
  `translationOfWork: {"@id": <original url>}` and the original `workTranslation`.
- `head()` gets an `og_type` parameter (`article` for posts).
- `copy_static()` also copies `posts/<id>/media/` to `dist/assets/posts/<id>/`.
- Products: category `meetings` (`CAT_NAME`, `CAT_TAG`, `CAT_ICON`), product `fofoca` with a
  `mic` icon, AI + open-source badges, CTA to GitHub; the product card gains an optional
  "Read the post" link when a post names it.

### `assets/styles.css`
Post list, prose (tables, blockquote, code, images), embed iframe, cover, translation banner and
badge, product card — all from existing tokens, so spec 007's restyle carries over.

### Tests (`tests/test_posts.py`)
Both post pages and both index pages exist; canonical/hreflang pair the two languages; header and
footer link Posts; the sitemap lists all four URLs; `BlogPosting` JSON-LD parses and the EN one
has `translationOfWork`; the EN page has the banner and links the original; tables, links and the
embed iframe render; media is copied; the published benchmark page contains no `/mnt/`, `/tmp/`
or `~/.config` paths; fo-foca appears under the new products area.

### Deploy
After merge: `ISKERU_SSH=<user@box> ISKERU_PATH=/var/www/iskeru ./deploy.sh`.

## Known Gaps

- The demo GIF is added when the file exists (`posts/fofoca/media/demo.gif` + one `![…](demo.gif)`
  line under the TL;DR in both languages).
- Translation is done by Claude at authoring time, not by the build; a changed original needs a
  re-translation by hand.
- No RSS feed, no tag pages, no "latest posts" block on the homepage yet.
- Spec 007's restyle is independent; posts ship in the current look and follow 007 when it lands.
