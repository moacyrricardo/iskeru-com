# 006 — Search Console: sitemap + GA4 link (property already verified)

> Status: **todo** · **owner-executed (not autopilot-buildable)** — on the default path there is
> no `build.py` change; "done" is console actions + evidence, not a code PR.
> Branch: _tbd_ · No Linear ticket.
>
> Revised after an adversarial red-team + **live DNS/HTTP checks** (see `## Red-team resolutions`).
> The first draft decided a DNS action without looking at DNS; ground truth changed the scope.

## Context

Analytics (spec 004) measures on-site behaviour; it can't show what happens on **Google Search
before the click** — queries, impressions, CTR, position, indexing health. That lives only in
**Google Search Console (GSC)**. This is the "which searches find the site" ask deferred from spec
005 (§Companion).

**Ground truth (verified live, not just from the repo):**
- **The site is already verified.** A `google-site-verification=DK_VFGarCgPre…` **TXT record already
  exists** on `iskeru.com`, and the owner confirms the GSC property is **theirs and verified**. So
  the original draft's headline step — "add a DNS TXT record and verify" — is a **no-op**. Do not
  add or remove records (Google periodically re-confirms; deleting the TXT would un-verify).
- **`www.iskeru.com` serves.** It resolves to Cloudflare and returns **HTTP 200** (the red-team's
  "NXDOMAIN" claim was wrong — re-checked live). So spec 005's plan to broaden the analytics
  host-gate to `www` is **not** moot. New sub-item: confirm `www` **canonicalises to apex** (all
  canonicals/`SITE` are `https://iskeru.com`) so `www` serving 200 isn't duplicate content.
- **Served `robots.txt` ≠ repo `robots.txt`.** Cloudflare injects a **managed** robots.txt
  (Content-Signals policy + `Disallow: /` for AI crawlers like GPTBot/ClaudeBot/CCBot/Google-Extended).
  The repo's `Sitemap:` line survives at the bottom and **Googlebot Search is not blocked**
  (Google-Extended affects AI training only), so search indexing is fine — but repo state is not
  served state.
- `render_sitemap()` emits **12 `<loc>`** (6 routes × 2 languages), hreflang alternates with a valid
  `pt-BR` + `x-default`→EN, 404 correctly excluded. `robots.txt` (repo) advertises the sitemap.
- GA4 (`G-H4S91E1LWD`) is already installed in `head()` via `ga_head()`.

## Decision

Since verification is done, 006 is three small owner actions plus one cleanup — **no default-path
code**.

1. **Confirm the existing GSC property and its type.** Check which property backs the existing token
   (a **Domain** property covers apex + `www` + `/pt/` + protocols; a **URL-prefix** property covers
   only its exact prefix). If it's URL-prefix on apex, consider also adding a Domain property (still
   zero DNS work if the TXT is already present) so `www` and future subdomains are covered.
2. **Submit / confirm the sitemap** in GSC (Sitemaps → `sitemap.xml`). No repo change — `robots.txt`
   already references it and the file is correct.
3. **Link GSC ↔ GA4** (GA4 Admin → Product links → Search Console links, then add the Search Console
   report collection so it's actually visible). This is the real value: it **joins** GSC's query and
   organic-landing-page dimensions with GA4 metrics (engagement, and — once spec 005 lands — key
   events) into a combined view **that does not exist inside GSC alone**. *Prerequisites:* Editor on
   the GA4 property **and** verified-owner on the GSC property, in the **same Google account**; one
   GSC property links to one GA4 web stream. (Correcting the first draft's false "adds no data GSC
   already has.")
4. **Cleanup: `www` canonicalisation.** Confirm `www.iskeru.com` either 301s to apex or serves with a
   `rel=canonical` to apex (the pages already emit apex canonicals, so Google should dedupe — but
   verify). If undesired, add a Cloudflare `www→apex` redirect rule. Small SEO hygiene, in-scope
   because it touches the same www question.

## Implementation

- **Out-of-repo (owner), documented in the PR/evidence:** confirm property + type; submit sitemap;
  create the GA4↔GSC link and enable the report collection; confirm/settle `www` canonicalisation.
- **Repo surface: none on the default path.** The `google-site-verification` **meta-tag** method in
  `head()` is retained only as a *contingency* if the site ever needs re-verification without DNS —
  and even then, **GA-based verification is the zero-work option** (the `gtag.js` snippet is already
  in `head()`; needs Editor on the GA property + same account). Caveat: 004's `config()` sits inside
  a host-gate `if`, and Google wants the snippet "unmodified", so GA verification *can* be flaky — the
  meta tag is the deterministic code fallback. If the meta tag is ever added, note the **spec 003
  interaction** (003 rewrites `head()`) and protect the tag with a unit test.
- **Machine-checked evidence (scriptable, add to the PR):** a small live-check — `dig +short
  iskeru.com TXT | grep google-site-verification` present; `sitemap.xml` and `robots.txt` return 200;
  every sitemap `<loc>` returns 200; a bogus path returns 404 — so the "done" PR carries at least one
  verified fact instead of only screenshots. The repo's `live-verify:test-flow-headless` agent (used
  by 005) can run it.

## Red-team resolutions

- **F1 (Critical) — TXT already exists / already verified:** confirmed live and by the owner;
  Decision no longer adds any DNS record; warns against deleting the TXT.
- **F2 (High) — missed GA-based verification:** now enumerated and ranked above the meta tag (both are
  only contingencies since verification is already done).
- **F3 (High) — overstated "not verifiable":** added the scriptable live-check (dig/sitemap/robots/200s).
- **F4 (Medium) — "www is NXDOMAIN":** **the red-team was wrong** — `www` serves HTTP 200 (re-checked);
  spec now records that and adds the canonicalisation cleanup, and confirms 005's www host-gate is real.
- **F5 (Medium) — "adds no data":** corrected — the link joins GSC dims with GA4 metrics; prerequisites named.
- **F6 (Medium) — Cloudflare-managed robots.txt:** documented; Googlebot/Search unaffected.
- **F7 (Medium) — ship-workflow mismatch:** spec marked **owner-executed / not autopilot-buildable**.
- **F8 (Low) — "Domain property answers apex-vs-www":** claim dropped; it aggregates search data, it
  doesn't determine serving behaviour (now answered directly: www serves 200).
- **F9 (Low) — latency wording:** tightened in Known Gaps (16-month = retention window; verification
  near-instant; re-confirmation; indexing takes weeks).
- **F10/F11 (Nit):** sitemap `changefreq`/`priority` are ignored by Google and `lastmod` is absent —
  noted for if the file is ever touched; meta-tag "separate entries" overstatement corrected.

## Known Gaps

- **Console/link actions are owner-executed** and unverifiable from the repo beyond the live-check;
  the PR/evidence carries screenshots.
- **Latency:** GSC typically shows history from before verification (up to the 16-month retention
  window); finalized query data (and the copy surfaced inside GA4) lags ~2–3 days; **indexing of a
  small site can take weeks**, not days.
- **GA4↔GSC link** surfaces Google-organic only and is subject to GSC anonymised-query thresholds —
  long-tail queries never appear.
- **`www` duplicate-content** risk until canonicalisation is confirmed (Decision #4).
- **Bing / IndexNow** out of scope (Google-only).

## Verification

- Live-check script passes: verification TXT present; `sitemap.xml`/`robots.txt`/all 12 `<loc>` URLs
  return 200; bogus path returns 404.
- GSC shows the property **Verified**, `sitemap.xml` **Success** with 12 URLs, and pages under
  **Indexed** (allow weeks).
- GA4 → Reports shows a **Search Console** collection (Queries / Google-organic landing pages) after
  the link + ~2–3 day lag.
- `www.iskeru.com` confirmed to canonicalise to apex (301 or `rel=canonical`).
- Save GSC (property + sitemap + first Queries) and the GA4 link screenshots under `specs/evidence/`.
