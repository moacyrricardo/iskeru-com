"""Regression tests for spec 004 — GA4 with Consent Mode v2 + consent banner.

Stdlib only (unittest), matching the zero-dependency policy of build.py. Run with:

    python3 -m unittest discover -s tests

The suite imports build.py and generates the whole site into a temporary
directory, asserting the analytics/consent invariants the spec depends on:
the Measurement ID appears on every page, Consent Mode v2 defaults run
(analytics denied) *before* the gtag/js tag loads, a clean build with an empty
ID emits no analytics at all, and the new privacy page exists in both languages
and is advertised in the sitemap.
"""

import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import build  # noqa: E402


def _build_into(tmp):
    """Run the generator with DIST pointed at a throwaway directory."""
    build.DIST = tmp
    build.main()


def _all_html(root):
    pages = []
    for r, _, files in os.walk(root):
        pages += [os.path.join(r, f) for f in files if f.endswith(".html")]
    return pages


class AnalyticsConsentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._orig_dist = build.DIST
        cls._orig_id = build.GA_MEASUREMENT_ID
        cls._tmp = tempfile.mkdtemp(prefix="iskeru-ga-test-")
        _build_into(cls._tmp)
        cls.pages = _all_html(cls._tmp)

    @classmethod
    def tearDownClass(cls):
        build.DIST = cls._orig_dist
        build.GA_MEASUREMENT_ID = cls._orig_id
        import shutil
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def test_measurement_id_on_every_page(self):
        """Every generated page carries the GA4 Measurement ID (site-wide tag)."""
        self.assertTrue(self.pages, "no pages were generated")
        for p in self.pages:
            html = open(p, encoding="utf-8").read()
            self.assertIn(build.GA_MEASUREMENT_ID, html,
                          f"{os.path.relpath(p, self._tmp)} missing Measurement ID")

    def test_consent_default_precedes_gtag_js(self):
        """Order invariant: the Consent Mode `consent 'default'` call must appear
        before the gtag/js loader on every page, or Consent Mode does nothing."""
        for p in self.pages:
            html = open(p, encoding="utf-8").read()
            i_default = html.find("'consent', 'default'")
            i_tag = html.find("googletagmanager.com/gtag/js")
            self.assertNotEqual(i_default, -1,
                                f"{os.path.relpath(p, self._tmp)} has no consent default")
            self.assertNotEqual(i_tag, -1,
                                f"{os.path.relpath(p, self._tmp)} has no gtag/js tag")
            self.assertLess(i_default, i_tag,
                            f"{os.path.relpath(p, self._tmp)}: consent default must precede gtag/js")

    def test_default_block_denies_analytics_storage(self):
        """The default consent block ships analytics_storage denied."""
        html = open(os.path.join(self._tmp, "index.html"), encoding="utf-8").read()
        block = re.search(r"'consent', 'default',\s*\{(.*?)\}", html, re.DOTALL)
        self.assertIsNotNone(block, "no consent default block found")
        self.assertIn("'analytics_storage': 'denied'", block.group(1))

    def test_config_call_is_host_gated(self):
        """The config() call is gated to the production host so dev/preview
        traffic never reaches GA."""
        html = open(os.path.join(self._tmp, "index.html"), encoding="utf-8").read()
        self.assertIn("location.hostname === 'iskeru.com'", html)

    def test_consent_banner_present_bilingual(self):
        """The Accept/Decline banner ships on both language home pages, with the
        Consent Mode update wired to analytics_storage granted."""
        for rel in ("index.html", "pt/index.html"):
            html = open(os.path.join(self._tmp, rel), encoding="utf-8").read()
            self.assertIn('id="consent-banner"', html, rel)
            self.assertIn('id="consent-accept"', html, rel)
            self.assertIn('id="consent-decline"', html, rel)
            self.assertIn("'analytics_storage': 'granted'", html, rel)

    def test_privacy_route_both_languages(self):
        """The privacy page is generated at /privacy/ and /pt/privacidade/."""
        for rel in ("privacy/index.html", "pt/privacidade/index.html"):
            self.assertTrue(os.path.isfile(os.path.join(self._tmp, rel)),
                            f"missing generated privacy page: {rel}")

    def test_privacy_in_sitemap(self):
        """Both privacy URLs are advertised in sitemap.xml."""
        sm = open(os.path.join(self._tmp, "sitemap.xml"), encoding="utf-8").read()
        for loc in ("https://iskeru.com/privacy/", "https://iskeru.com/pt/privacidade/"):
            self.assertIn(f"<loc>{loc}</loc>", sm, loc)

    def test_empty_id_emits_no_analytics(self):
        """Clean-build invariant: with an empty Measurement ID, no page contains
        googletagmanager.com and no consent banner is emitted."""
        tmp = tempfile.mkdtemp(prefix="iskeru-noga-test-")
        saved = build.GA_MEASUREMENT_ID
        try:
            build.GA_MEASUREMENT_ID = ""
            _build_into(tmp)
            pages = _all_html(tmp)
            self.assertTrue(pages, "no pages were generated for empty-ID build")
            for p in pages:
                html = open(p, encoding="utf-8").read()
                self.assertNotIn("googletagmanager.com", html,
                                 f"{os.path.relpath(p, tmp)} leaked analytics with empty ID")
                self.assertNotIn('id="consent-banner"', html,
                                 f"{os.path.relpath(p, tmp)} leaked consent banner with empty ID")
        finally:
            build.GA_MEASUREMENT_ID = saved
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
