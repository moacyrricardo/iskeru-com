"""Regression tests for spec 002 — intent-matched SEO service pages.

Stdlib only (unittest), matching the zero-dependency policy of build.py. Run with:

    python3 -m unittest discover -s tests

The suite imports build.py, generates the whole site into a temporary directory,
and asserts the on-page SEO invariants the spec depends on: the four new bilingual
pages exist, canonical/hreflang are correct, the new pages are in sitemap.xml (and
the 404 is not), every emitted JSON-LD block is valid JSON with the right schema
nodes, titles/H1s carry the literal target phrases, and meta descriptions stay
within the 155-character limit.
"""

import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import build  # noqa: E402

LD_RE = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.DOTALL)


def _build_into(tmp):
    """Run the generator with DIST pointed at a throwaway directory."""
    build.DIST = tmp
    build.main()


class SeoServicePagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._orig_dist = build.DIST
        cls._tmp = tempfile.mkdtemp(prefix="iskeru-test-")
        _build_into(cls._tmp)
        cls.html = {}
        cls.new = {
            "en fractional": "fractional-cto/index.html",
            "pt fractional": "pt/cto-fracional/index.html",
            "en custom": "custom-development/index.html",
            "pt custom": "pt/desenvolvimento/index.html",
        }
        for label, rel in cls.new.items():
            path = os.path.join(cls._tmp, rel)
            if os.path.isfile(path):
                cls.html[label] = open(path, encoding="utf-8").read()

    @classmethod
    def tearDownClass(cls):
        build.DIST = cls._orig_dist
        import shutil
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def test_new_pages_exist_both_languages(self):
        for label, rel in self.new.items():
            self.assertTrue(os.path.isfile(os.path.join(self._tmp, rel)),
                            f"missing generated page: {rel}")

    def test_canonical_and_hreflang(self):
        cases = {
            "en fractional": "https://iskeru.com/fractional-cto/",
            "pt fractional": "https://iskeru.com/pt/cto-fracional/",
            "en custom": "https://iskeru.com/custom-development/",
            "pt custom": "https://iskeru.com/pt/desenvolvimento/",
        }
        for label, canon in cases.items():
            h = self.html[label]
            self.assertIn(f'<link rel="canonical" href="{canon}" />', h, label)
            self.assertIn('hreflang="pt-BR"', h, label)
            self.assertIn('hreflang="x-default"', h, label)

    def test_og_image_and_large_twitter_card(self):
        og = "https://iskeru.com/assets/og-image.png"
        for label, h in self.html.items():
            self.assertIn(f'<meta property="og:image" content="{og}" />', h, label)
            self.assertIn('<meta name="twitter:card" content="summary_large_image" />', h, label)
            self.assertIn(f'<meta name="twitter:image" content="{og}" />', h, label)

    def test_all_jsonld_blocks_are_valid(self):
        pages = []
        for r, _, files in os.walk(self._tmp):
            pages += [os.path.join(r, f) for f in files if f.endswith(".html")]
        total = 0
        for p in pages:
            for block in LD_RE.findall(open(p, encoding="utf-8").read()):
                total += 1
                obj = json.loads(block)  # raises on invalid JSON -> test failure
                self.assertEqual(obj.get("@context"), "https://schema.org")
                self.assertIn("@graph", obj)
        self.assertGreater(total, 0, "no JSON-LD blocks were emitted")

    def test_service_pages_have_expected_schema_nodes(self):
        for label, h in self.html.items():
            graph = json.loads(LD_RE.search(h).group(1))["@graph"]
            types = {n.get("@type") for n in graph}
            self.assertEqual({"Person", "ProfessionalService", "FAQPage"} - types, set(),
                             f"{label}: missing schema nodes, got {types}")

    def test_titles_and_h1_contain_literal_phrases(self):
        cases = {
            "en fractional": ("Fractional CTO for Hire", "Fractional CTO for hire"),
            "pt fractional": ("CTO Fracional", "CTO Fracional"),
            "en custom": ("Custom Software", "Custom project development"),
            "pt custom": ("Desenvolvimento", "Desenvolvimento de projetos sob medida"),
        }
        for label, (title_phrase, h1_phrase) in cases.items():
            h = self.html[label]
            title = re.search(r"<title>(.*?)</title>", h).group(1)
            h1 = re.search(r"<h1>(.*?)</h1>", h).group(1)
            self.assertIn(title_phrase, title, f"{label} title")
            self.assertIn(h1_phrase, h1, f"{label} h1")

    def test_meta_descriptions_within_155(self):
        for label, h in self.html.items():
            desc = re.search(r'<meta name="description" content="(.*?)" />', h).group(1)
            self.assertLessEqual(len(desc), 155, f"{label} desc len {len(desc)}: {desc!r}")

    def test_sitemap_includes_service_pages_excludes_404(self):
        sm = open(os.path.join(self._tmp, "sitemap.xml"), encoding="utf-8").read()
        for loc in ["https://iskeru.com/fractional-cto/",
                    "https://iskeru.com/pt/cto-fracional/",
                    "https://iskeru.com/custom-development/",
                    "https://iskeru.com/pt/desenvolvimento/"]:
            self.assertIn(f"<loc>{loc}</loc>", sm, loc)
        self.assertNotIn("404", sm)

    def test_service_pages_priority_high(self):
        sm = open(os.path.join(self._tmp, "sitemap.xml"), encoding="utf-8").read()
        m = re.search(r"<loc>https://iskeru.com/fractional-cto/</loc>.*?<priority>(.*?)</priority>",
                      sm, re.DOTALL)
        self.assertEqual(m.group(1), "0.9")

    def test_home_links_to_service_pages_with_keyword_anchors(self):
        home = open(os.path.join(self._tmp, "index.html"), encoding="utf-8").read()
        self.assertIn('href="/fractional-cto/"', home)
        self.assertIn("Fractional CTO", home)
        self.assertIn('href="/custom-development/"', home)
        self.assertIn("Custom development", home)

    def test_each_service_page_has_at_least_four_faq_items(self):
        for label in ("en fractional", "pt fractional", "en custom", "pt custom"):
            self.assertGreaterEqual(self.html[label].count('<details class="faq-item">'), 4, label)


if __name__ == "__main__":
    unittest.main(verbosity=2)
