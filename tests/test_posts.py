"""Regression tests for spec 008 — bilingual posts with Claude-translated counterparts.

Stdlib only (unittest). Builds the whole site into a temporary directory and checks the
posts section: both languages render and point at each other, the translation is labelled,
the Markdown subset renders, structured data is valid, media is published (with no local
paths leaking), and fo-foca shows up on the products page.
"""

import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import build  # noqa: E402

LD_RE = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.DOTALL)
PAGES = {
    "pt_post": "pt/posts/construindo-fofoca/index.html",
    "en_post": "posts/building-fofoca/index.html",
    "pt_index": "pt/posts/index.html",
    "en_index": "posts/index.html",
}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class PostsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._orig_dist = build.DIST
        cls._tmp = tempfile.mkdtemp(prefix="iskeru-posts-")
        build.DIST = cls._tmp
        build.main()
        cls.html = {k: _read(os.path.join(cls._tmp, v)) for k, v in PAGES.items()}

    @classmethod
    def tearDownClass(cls):
        build.DIST = cls._orig_dist
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def read(self, rel):
        return _read(os.path.join(self._tmp, rel))

    def ld_nodes(self, page):
        nodes = []
        for block in LD_RE.findall(self.html[page]):
            nodes.extend(json.loads(block)["@graph"])
        return nodes

    # --- routing and language pairing ---------------------------------------
    def test_post_pages_point_at_each_other(self):
        for page, canon in (("pt_post", "https://iskeru.com/pt/posts/construindo-fofoca/"),
                            ("en_post", "https://iskeru.com/posts/building-fofoca/")):
            h = self.html[page]
            self.assertIn(f'<link rel="canonical" href="{canon}" />', h)
            self.assertIn('hreflang="en" href="https://iskeru.com/posts/building-fofoca/"', h)
            self.assertIn('hreflang="pt-BR" href="https://iskeru.com/pt/posts/construindo-fofoca/"', h)
            self.assertIn('<meta property="og:type" content="article" />', h)

    def test_lang_switch_goes_to_counterpart(self):
        self.assertIn('<a href="/posts/building-fofoca/">EN</a>', self.html["pt_post"])
        self.assertIn('<a href="/pt/posts/construindo-fofoca/">PT</a>', self.html["en_post"])

    def test_nav_and_footer_link_posts_on_every_page(self):
        for rel, href in (("index.html", "/posts/"), ("pt/index.html", "/pt/posts/"),
                          ("products/index.html", "/posts/")):
            self.assertGreaterEqual(self.read(rel).count(f'<a href="{href}">Posts</a>'), 2, rel)

    def test_sitemap_lists_posts(self):
        sm = self.read("sitemap.xml")
        for url in ("/posts/", "/pt/posts/", "/posts/building-fofoca/", "/pt/posts/construindo-fofoca/"):
            self.assertIn(f"<loc>https://iskeru.com{url}</loc>", sm)

    # --- translation labelling ------------------------------------------------
    def test_translation_is_labelled(self):
        en, pt = self.html["en_post"], self.html["pt_post"]
        self.assertIn('class="tr-banner"', en)
        self.assertIn("Automatically translated by Claude from Portuguese.", en)
        self.assertIn('href="/pt/posts/construindo-fofoca/" hreflang="pt-BR"', en)
        self.assertNotIn('class="tr-banner"', pt)
        self.assertIn("Translated by Claude", self.html["en_index"])
        self.assertNotIn("Traduzido pelo Claude", self.html["pt_index"])

    def test_structured_data(self):
        pt = next(n for n in self.ld_nodes("pt_post") if n["@type"] == "BlogPosting")
        en = next(n for n in self.ld_nodes("en_post") if n["@type"] == "BlogPosting")
        self.assertEqual(pt["inLanguage"], "pt-BR")
        self.assertEqual(en["inLanguage"], "en")
        self.assertEqual(en["translationOfWork"]["@id"], pt["@id"])
        self.assertEqual(pt["workTranslation"]["@id"], en["@id"])
        self.assertEqual(pt["author"]["@id"], build.PERSON_ID)
        self.assertTrue(pt["image"].endswith("/assets/posts/fofoca/fofoca-logo.png"))

    # --- Markdown rendering ---------------------------------------------------
    def test_markdown_subset_renders(self):
        pt = self.html["pt_post"]
        self.assertIn("<h2>Medindo antes de construir</h2>", pt)
        self.assertIn('<div class="table-wrap"><table>', pt)
        self.assertIn("<code>-dev 1</code>", pt)
        self.assertIn("<em>(provavelmente)</em>", pt)
        self.assertIn('<a href="https://moacyrricardo.github.io/skills/prototype-guide.html">/prototype</a>', pt)
        self.assertIn('<a href="https://github.com/moacyrricardo/fofoca">github.com/moacyrricardo/fofoca</a>', pt)
        self.assertNotIn("**", pt)
        self.assertNotIn("*(embed", pt)

    def test_markdown_escapes_html(self):
        out = build.render_markdown("a <script>x</script> & b", "fofoca", "t")
        self.assertIn("&lt;script&gt;", out)
        self.assertNotIn("<script>", out)

    def test_embed_points_at_published_media(self):
        for page in ("pt_post", "en_post"):
            self.assertIn('<iframe src="/assets/posts/fofoca/benchmarks-mx230.html"', self.html[page])
        self.assertTrue(os.path.isfile(os.path.join(self._tmp, "assets/posts/fofoca/benchmarks-mx230.html")))
        self.assertTrue(os.path.isfile(os.path.join(self._tmp, "assets/posts/fofoca/fofoca-logo.png")))

    def test_demo_gif_under_tldr(self):
        for page, alt in (("pt_post", "fo-foca funcionando"), ("en_post", "fo-foca in action")):
            h = self.html[page]
            img = h.index(f'<img src="/assets/posts/fofoca/demo.gif" alt="{alt}"')
            self.assertLess(h.index("TL;DR"), img)
            self.assertLess(img, h.index("<h2>"))
        self.assertTrue(os.path.isfile(os.path.join(self._tmp, "assets/posts/fofoca/demo.gif")))

    def test_published_benchmark_has_no_local_paths(self):
        bench = self.read("assets/posts/fofoca/benchmarks-mx230.html")
        for leak in ("/mnt/", "/tmp/", "~/.config", "qwenb", "your recording"):
            self.assertNotIn(leak, bench)

    def test_stylesheet_url_changes_with_its_content(self):
        # /assets/* is cached for 7 days (browser + Cloudflare); the URL must carry a
        # content hash or new styles never reach visitors (seen live after spec 008).
        import hashlib
        with open(os.path.join(ROOT, "assets", "styles.css"), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()[:10]
        for page in self.html.values():
            self.assertIn(f'href="/assets/styles.css?v={digest}"', page)
        self.assertIn(f'href="/assets/styles.css?v={digest}"', self.read("404.html"))

    def test_written_date_and_order(self):
        pt = self.read("pt/posts/ia-escreve-1k-linhas/index.html")
        en = self.read("posts/ai-writes-1k-lines/index.html")
        self.assertIn(">20 nov 2026</time> · escrito em set 2026 · 5 min de leitura", pt)
        self.assertIn(">Nov 20, 2026</time> · written Sep 2026 · 5 min read", en)
        self.assertIn('"dateCreated": "2026-09"', en)
        idx = self.html["pt_index"]
        self.assertLess(idx.index("/pt/posts/ia-escreve-1k-linhas/"), idx.index("/pt/posts/construindo-fofoca/"))
        self.assertIn("escrito em set 2026", idx)

    # --- product link ---------------------------------------------------------
    def test_fofoca_on_products_page(self):
        prod = self.read("pt/produtos/index.html")
        self.assertIn('<section id="meetings"', prod)
        self.assertIn('<article id="fofoca"', prod)
        self.assertIn('href="/pt/posts/construindo-fofoca/"', prod)
        self.assertIn('href="/pt/produtos/#fofoca"', self.html["pt_post"])

    def test_index_lists_post_with_summary(self):
        self.assertIn('href="/pt/posts/construindo-fofoca/"', self.html["pt_index"])
        self.assertIn("Daí surgiu o fo-foca.", self.html["pt_index"])


if __name__ == "__main__":
    unittest.main()
