# 005 — GA4 interaction events: profile/repo/contact funnel + engagement

> Status: **todo**
> Branch: _tbd_ · No Linear ticket.
>
> Revised after an adversarial red-team of the first draft (see `## Red-team resolutions`).
> Edit sites are cited **by function name**, not line number — spec 004 already shifted
> `build.py` once and spec 003 (still `todo`) will shift `head()` again.

## Context

Spec 004 shipped GA4 with **advanced** Consent Mode v2: `gtag.js` loads and `gtag('config', …)`
runs on the production host **regardless of consent**, while `analytics_storage` stays `denied`
until the visitor accepts the banner. Enhanced Measurement already gives page views, sessions,
scroll, generic outbound `click`, and engagement time out of the box. This spec turns that into
**directional** behavioural signal — explicitly not a complete census (see the consent-bias gap
below):

1. **A click funnel to the owner's destinations** — the personal **GitHub profile**
   (`github.com/moacyrricardo`) and **LinkedIn** (`linkedin.com/in/moacyrricardo`), the OSS **repo**
   links, and the **contact email** (`mailto:contato@iskeru.com`).
2. **Which pages hold attention** — engagement time / scroll per page (reporting, no code).
3. **Which search queries find the site** — deferred; that's Search Console, not GA (see §Companion).

**What's already captured (no code):** outbound http(s) clicks (Enhanced Measurement's generic
`click`), scroll, and engagement time. **`mailto:` clicks are NOT auto-tracked** by Enhanced
Measurement (it covers off-domain http(s) links and downloads only) — so the contact event needs
code. Engagement time is a *reporting* task (§Reporting).

**The link inventory (verified against `build.py`) — a naive `hostname==='github.com'` check is wrong.**
There are **seven** github.com links plus one `github.io`, only one of which is the profile:

| Link | Where | Classify as |
|------|-------|-------------|
| `github.com/moacyrricardo` (profile) | about buttons, about list, OSS "all" link | `profile_click` / github |
| `linkedin.com/in/moacyrricardo` (profile) | about buttons, about list | `profile_click` / linkedin |
| `github.com/moacyrricardo/<repo>` ×6 | OSS repo cards (`GITHUB_PROJECTS`) | `repo_click` |
| `github.com/moacyrricardo/compute-admin` | a product CTA | `repo_click` |
| `moacyrricardo.github.io/skills` | the skills product CTA | `repo_click` |
| `mailto:contato@iskeru.com` | home `#contact`, about, site-wide CTA band, product CTAs, privacy page | `contact_click` |

So classification must key on **host + path**, not host alone (owner decision: *separate events* for
profile vs repo).

## Decision

Add three explicit GA4 events via **one delegated click listener**, keep advanced consent mode but
**disclose interaction tracking on the privacy page**, broaden the host-gate to `www`, and drive the
funnel/engagement analysis from the GA4 console.

1. **`profile_click`** — `{ network: 'github' | 'linkedin', link_location }` — only the owner's
   profile URLs: `github.com` path **exactly** `/moacyrricardo`, and `linkedin.com`/`www.linkedin.com`
   path under `/in/`.
2. **`repo_click`** — `{ repo: '<name>', link_location }` — `github.com` paths **deeper than**
   `/moacyrricardo/…` (repo name = 2nd path segment), plus `moacyrricardo.github.io/*` (repo = 1st
   segment, e.g. `skills`).
3. **`contact_click`** — `{ method: 'email', product: '<subject-or-none>', link_location }` — any
   `mailto:` link. `product` is parsed from the `?subject=` already present on product-CTA mailtos
   (`…?subject=hive` etc.) — the highest-value conversion, and it's free in the href.
4. **One delegated listener**, emitted as its **own `<script>` element** (NOT appended to the
   existing footer script, which is deliberately ES5): listen for both **`click` and `auxclick`**
   (middle-click opens repos/profiles in a new tab — a developer habit), resolve
   `event.target.closest('a')` (clicks land on the SVG icon inside the anchor), wrap URL parsing in
   `try/catch` (an `<a>` with no href yields `a.href === ''`), and classify by protocol/host/path per
   #1–#3. `gtag` always exists (defined in `ga_head()`); Consent Mode governs collection, so no
   per-event consent check. **The listener may use modern JS since it's its own script tag** — but
   keep it dependency-free.
5. **`link_location`** comes from `data-loc` on the *container* of each relevant link, resolved via
   `closest('[data-loc]')` with a `'other'` fallback. Hints go on the **actual** link sites (see
   Implementation) — NOT the footer, which contains no social/mailto links.
6. **Broaden the host-gate** in `ga_head()`: replace the exact `location.hostname === 'iskeru.com'`
   with an **explicit allowlist** `['iskeru.com', 'www.iskeru.com'].indexOf(location.hostname) !== -1`
   (preferred over an open `/(^|\.)iskeru\.com$/` suffix, which would silently opt every future
   `staging.`/`preview.` subdomain into production data). **Verify first** whether `www` even serves
   pages or 301s to apex (all canonicals/`SITE` are apex) — if it 301s, this change is a harmless
   no-op but still correct defensively.
7. **Privacy page update** (owner decision: keep advanced mode + disclose): extend `render_privacy`
   and its EN/PT `T` strings to state that the site records anonymous **interaction events** (clicks
   on profile/repo/contact links) and that, because analytics runs in advanced consent mode, a
   **cookieless** signal may be sent to Google even before/without consent, while cookies remain
   gated on Accept.
8. **GA4 console (out-of-repo, documented in the PR):** mark `profile_click`, `repo_click`,
   `contact_click` as **Key events**; register **custom dimensions** for `network`, `repo`,
   `method`, `product`, `link_location` (else they only show in Realtime/DebugView, not standard
   reports); build a **funnel exploration** (landing → engaged content `page_view` → a click event),
   broken down by the params. Event-level **retention is 2 or 14 months** (there is no "30-day"
   setting) — set 14 months so funnel lookback isn't capped at 004's 2-month default.

## Implementation

- **`build.py` — new delegated-listener script:** add a helper (e.g. `interaction_events_js()`)
  emitting a standalone `<script>` included by `page()`/`footer()` on every page. Classify with
  `new URL(a.href)` inside `try/catch`; branch on `u.protocol === 'mailto:'` → `contact_click`
  (parse `u.searchParams.get('subject')`); `u.hostname` github/linkedin/github.io + path checks →
  `profile_click`/`repo_click` per Decision #1–#3. Bind `click` and `auxclick`. Do **not** touch the
  existing ES5 footer `<script>` inside `footer()`.
- **`build.py` — `data-loc` hints** on the containers that actually hold these links: the about
  profile-button group and the about contact list, the OSS "all projects" link/block, the home
  `#contact` block, the site-wide CTA band, the per-product CTA wrappers (so `contact_click.product`
  is corroborated by `link_location`), and the privacy-page contact line. No change to the `<a>` tags.
- **`build.py` — `ga_head()`:** swap the host-gate to the allowlist (Decision #6). This is the only
  edit to 004's shipped GA/consent code; note the interaction with spec 003, which will also rewrite
  `head()`/`ga_head()`.
- **`build.py` — `render_privacy` + `T`:** add the interaction-tracking disclosure sentence, EN and
  PT‑BR (Decision #7).
- **Tests (`tests/test_interaction_events.py`, stdlib unittest):** (a) build asserts — the listener
  script is emitted on every `dist/**/*.html`, references all three event names, binds `auxclick`,
  and wraps parsing in `try`; the host-gate allowlist string is present and the old exact-match is
  gone; `data-loc` hints appear on the expected containers and NOT on `footer`; the privacy pages
  (EN+PT) contain the disclosure. (b) **Behavioural assert (automated, not manual):** drive the
  built site with the repo's headless **`live-verify:test-flow-headless`** agent — click the About
  GitHub profile button, a repo card, and a `mailto:` link, and assert `window.dataLayer` gained
  `profile_click` / `repo_click` / `contact_click` with the right params (localhost won't transmit —
  host-gate — so assert on `dataLayer`, not GA).
- **Out-of-repo (owner), in the PR:** Key events; custom dimensions; funnel exploration; 14-month
  retention. To see events live during verification, use **`debug_mode`/the GA Debugger extension**
  (prod events do **not** appear in DebugView otherwise) or watch **Realtime → Events**.

## Reporting (no code — "which pages hold attention")

GA4 **Reports → Engagement → Pages and screens**: read **Average engagement time** and **Views** per
`page_path`, sort by engagement to find the stickiest pages; complement with the `scroll` event
(Enhanced Measurement, 90% depth) for read-through. Caveat: low-volume pages can show `(not set)` /
thresholded rows until traffic accrues.

## Companion (ask #3 — search queries)

Search queries that lead to iskeru.com come from **Google Search Console**, not GA events.
**Recommend a separate spec 006 — Search Console verification + GA4 link** (DNS/meta verification +
sitemap submission; `sitemap.xml` is already generated). Noted so the ask isn't lost.

## Red-team resolutions

- **Consent-bias ceiling (Critical):** with `analytics_storage` denied by default, declined-consent
  and never-answered-banner visitors yield **no funnel rows** (Google's behavioural modeling needs
  volumes a portfolio site won't hit), and the target audience (developers) is the cohort most likely
  to decline and to run adblockers that block `googletagmanager.com`. **The funnel measures consented,
  non-adblocked traffic only — a self-selected minority.** Framing throughout is "directional signal,"
  not "census." (See Known Gaps.)
- **github.com over-matching (Critical):** resolved by host+path classification and *separate*
  `profile_click`/`repo_click` events (Decision #1–#3), so repo-card and product-CTA clicks no longer
  pollute the profile funnel.
- **Pre-consent pings + privacy (High):** owner chose to keep advanced consent mode and **disclose**
  interaction tracking on the privacy page (Decision #7).
- **Stale citations (fix):** all edit sites now cited by function name.
- **ES5 vs modern JS (Medium):** the listener is its **own** `<script>`, never appended to the ES5
  footer script, so optional chaining etc. can't parse-break the nav-toggle/year script.
- **Host-gate premise/scope (Medium):** verify `www` serving first; use an explicit allowlist, not an
  open suffix, to avoid silent staging opt-in.
- **`data-loc` coverage (Medium):** hints moved to the real link containers (incl. product CTAs);
  footer dropped; `?subject=` exploited for `contact_click.product`.
- **Tests (Medium):** added an automated headless `dataLayer` behavioural assert beyond string checks.
- **Double-count (Low):** Enhanced Measurement outbound `click` stays **on**; profile/repo clicks
  therefore also appear as generic `click` — totals overlap by design; the named events are the funnel
  source of truth.
- **DebugView / retention (Low):** removed the bogus "30-day retention"; documented `debug_mode` for
  live verification and 14-month retention for lookback.

## Known Gaps

- **Consent + adblock bias** (above) — the dominant validity limit on *every* deliverable here.
- **`contact_click` is mail-client intent, not contact** — the email is also visible text people
  copy-paste; some browsers have no `mailto:` handler; a click never confirms a sent mail. Expect
  undercount of true contacts.
- **Funnel/Key-event/custom-dimension/retention setup is console-only** — unverifiable from the repo;
  the PR documents the steps and shows events firing (Realtime/DebugView with `debug_mode`).
- **Custom-dimension backfill:** params populate standard reports only *after* the dimensions are
  registered; earlier hits lack them.
- **New subdomains won't track** (explicit allowlist) — intentional; add hosts deliberately.
- **Search Console (ask #3)** deferred to spec 006.
- **Bots/self-clicks** inflate click events; 004's internal-traffic filter mitigates, not eliminates.

## Verification

- `python3 -m unittest discover -s tests` passes (build asserts) and the headless behavioural test
  confirms the three events reach `dataLayer` with correct params on localhost.
- Production after deploy: with `debug_mode`/GA Debugger (or Realtime → Events), click a profile link,
  a repo card, and a `mailto:` (incl. a product CTA to check `product`), and confirm
  `profile_click`/`repo_click`/`contact_click` arrive with correct params; confirm `www.iskeru.com`
  now tracks (or that it 301s to apex). Save DebugView + funnel screenshots under `specs/evidence/`.
