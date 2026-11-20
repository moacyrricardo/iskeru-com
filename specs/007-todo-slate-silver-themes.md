# 007 — Slate & Silver themes: outline buttons, system-following with a toggle

> Status: **todo**
> Branch: _tbd_ · No Linear ticket.
>
> **Design reference (source of truth for values):**
> [`007-assets/dark-eb-styles.css`](007-assets/dark-eb-styles.css) (dark — "E-B Cool slate, outline") and
> [`007-assets/light-hb-styles.css`](007-assets/light-hb-styles.css) (light — "H-B Silver light, outline").
> Both are full copies of `assets/styles.css` with only colour, font, button, hero-background and
> card-hover rules changed. Side-by-side comparison (private):
> https://claude.ai/artifact/T2aVQQo4YGzsuvHdedDgLj

## Context

The current look — navy-black `#0b0d12`, gold/amber gradient accent, gold radial glows in the hero,
glowing gradient primary button, Inter + Space Grotesk — reads as the generic "Linear / AI-SaaS"
aesthetic and is visibly close to Matt Pocock's aihero.dev (near-black `#14161a` + gold `#f5c451`).
The owner wants a restrained, black-or-grey look that fits an engineering leader's personal page.

The exploration (2026-11-13) was deliberately constrained to **colours, fonts and the
button/gradient treatment only** — layout, spacing, sizes, HTML and copy were held fixed. Research
on the gradient/glow button (LogRocket "Linear design" 2025, Rectangle "The Linear effect", GitHub
Primer and GOV.UK button guidance) concluded the gradient carries no meaning and dilutes the brand;
mature systems use one plain primary action. The owner picked the **outline** treatment in two
palettes and wants **both**, as dark and light themes.

## Decision

1. **Two themes, one stylesheet.**
   - **Dark = Cool slate:** bg `#23272d`, surface `#2c3138`, text `#e7ebf0`, accent ice-blue `#a9c7dc`.
   - **Light = Silver light:** bg `#d6d7d8`, surface `#e1e2e3`, text `#1a1b1e`, accent wine `#6e1f2f`.
   - Full token values: the two asset files' `:root` blocks.
2. **Theme selection:** follow the OS (`prefers-color-scheme`) by default; a header toggle
   overrides it and the choice is remembered per browser. **Dark is the fallback** when the OS
   expresses no preference (keeps the site's current dark-first identity).
3. **Fonts (both themes):** **Schibsted Grotesk** (display, 500/600/700) + **Instrument Sans**
   (body, 400/500/600/700). Replaces Inter + Space Grotesk. (The dark reference file still names
   Sora/Outfit — ignore those; fonts come from this decision.)
4. **No gradients or glows anywhere.** Buttons use the outline treatment:
   - `.btn-primary`: transparent fill, `1px solid var(--accent)`, `color: var(--accent)`, no
     shadow, no lift. Hover: `var(--accent-soft)` fill. Active: `var(--accent)` fill +
     `var(--accent-ink)` text.
   - `.btn-ghost`: transparent, transparent 1px border (size unchanged), `color: var(--text)`.
     Hover: underline + `var(--accent)` colour.
   - Hero: radial blobs removed (`.hero::before` background `none`), 1px `--border-soft`
     hairline under `.hero`.
   - `.card:hover`: border-colour change only — no `translateY`, no shadow.
   - `--accent-grad` → `var(--accent)` (flattens `.brand-mark`, `.tl-dot`, `.badge-ai`); `--glow`
     → `none`; `.brand-mark` glow shadow removed.
5. **Unchanged:** layout, spacing, type sizes, radii, HTML structure, copy, `:focus-visible` and
   focus-ring styles, `.skip-link` behaviour.

## Implementation

All changes are in `assets/styles.css` and `build.py` (`head()`, `header()`, the inline consent
banner CSS, and the inline scripts). No new dependencies.

### 1. `assets/styles.css` — tokens for both themes

- Bare `:root` holds the **dark** tokens + `color-scheme: dark` (dark fallback).
- Light tokens are applied by:
  ```css
  @media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { /* light tokens */ color-scheme: light; } }
  :root[data-theme="light"] { /* same light tokens */ color-scheme: light; }
  ```
  No `[data-theme="dark"]` block is needed: bare `:root` is already dark, and the
  `:not([data-theme="dark"])` guard stops a light OS from overriding an explicit dark choice.
- **Tokenise every theme-dependent literal** found in rules today (diff of the two asset files
  lists them all, ~10). Add tokens for them, e.g.:
  `--header-bg` (`rgba(35,39,45,.72)` / `rgba(214,215,216,.78)`),
  `--header-bg-solid` (mobile menu, `…,.97`),
  `--skip-ink` (`#15202a` / `#fff`),
  `--card-hover-border` (`rgba(169,199,220,.5)` / `rgba(110,31,47,.45)`),
  `--ring-accent` (the `0 0 0 4px …0.12` ring colour),
  `--live-soft`, `--live-ring`, `--badge-live-bg`, `--badge-soon-bg`,
  `--banner-shadow` (consent banner).
  After this, no rule outside the token blocks may contain a theme-specific colour literal.
- Apply the outline-button / no-glow rules from Decision §4 once (they reference tokens only).
  Where the two reference files differ in non-colour details (H-B adds `box-shadow: none` on
  `.btn-primary` and `transform: none` on `:active`), take the **H-B** version for both themes so
  B buttons don't nudge on press.
- `--font-sans: "Instrument Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;`
  `--font-display: "Schibsted Grotesk", var(--font-sans);`

### 2. `build.py` — `head()`

- Replace the Google Fonts URL with
  `family=Instrument+Sans:wght@400;500;600;700&family=Schibsted+Grotesk:wght@500;600;700&display=swap`.
- Add, **before** the stylesheet link, a tiny blocking inline script that applies a stored choice
  so there is no flash of the wrong theme:
  ```html
  <script>try{var t=localStorage.getItem('iskeru_theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>
  ```
- Add `<meta name="color-scheme" content="dark light" />` and two theme colours:
  `<meta name="theme-color" content="#23272d" media="(prefers-color-scheme: dark)" />`,
  `<meta name="theme-color" content="#d6d7d8" media="(prefers-color-scheme: light)" />`.

### 3. `build.py` — `header()` toggle

- Add a `<button class="theme-toggle" type="button">` inside `.site-nav`, after the language
  switch, with an inline sun/moon icon via the existing `icon()` helper (add `sun` / `moon` glyphs
  if absent). Bilingual `aria-label` from `T[lang]`: EN "Switch to light theme" / "Switch to dark
  theme", PT "Mudar para tema claro" / "Mudar para tema escuro"; label reflects the *target* theme.
- Script (appended to the existing footer/inline script, ES5-safe like the consent code):
  determine the current effective theme (`data-theme` attribute, else
  `matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'`), on click flip it,
  set `data-theme`, `localStorage.setItem('iskeru_theme', …)` in try/catch, update `aria-label`
  and `aria-pressed`. Listen to the media query `change` event only while no stored choice
  exists, so the icon stays correct when the OS switches.
- Styling: same visual weight as `.lang-switch` items (text-dim colour, accent on hover, visible
  `:focus-visible`); inside the mobile menu it sits on its own row like the language switch.

### 4. Consent banner CSS (`build.py` ~line 841)

Replace `box-shadow:0 -8px 40px -12px rgba(0,0,0,.6)` with `var(--banner-shadow)`; it already uses
`--surface` / `--border`, so it themes automatically.

### 5. Privacy page

Add one sentence (EN + PT) that a theme preference may be stored in `localStorage`
(`iskeru_theme`) — functional, not tracking, never sent anywhere.

### 6. Tests (`tests/`, stdlib unittest)

- Built `index.html` (EN + PT) contains the new Google Fonts families and **not** Inter /
  Space Grotesk.
- Built pages contain the pre-paint theme script before `/assets/styles.css`, both `theme-color`
  metas, and a `.theme-toggle` button with the correct bilingual `aria-label`.
- `assets/styles.css`: no `linear-gradient(` / `radial-gradient(` remain; a `[data-theme="light"]`
  block and a `prefers-color-scheme: light` block both exist and define the same token names.
- Every token defined in the light blocks is also defined in bare `:root`.

### 7. Verification

Build, serve (`python3 build.py && python3 -m http.server -d dist 8000`) and check, at desktop
and 390px: OS dark, OS light, toggle both ways, reload keeps the choice, no flash on reload, PT
pages, 404 page, consent banner in both themes, keyboard focus visible on the toggle.

## Known Gaps

- **`og-image.png`** still uses the old navy/gold look — regenerate in a follow-up.
- **Spec 003** (self-hosted fonts, inline CSS) currently names Inter / Space Grotesk. When 003 is
  built after this, it self-hosts **Schibsted Grotesk + Instrument Sans** instead, and the inline
  theme script stays first in `<head>`. If 003 ships first, this spec swaps its self-hosted files.
- Product sites (boletim, minhabufunfa, Cevem.Ai) are not restyled.
- Content repositioning (profile-first homepage, entity/schema, copy) is separate work — see the
  2026-11-12 AI-visibility review; not part of this spec.
