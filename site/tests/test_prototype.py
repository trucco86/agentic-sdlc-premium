from html.parser import HTMLParser
from pathlib import Path
import unittest

HTML = Path(__file__).resolve().parents[1] / "index.html"

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.lang = None
        self.robots = None
        self.title_found = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content")

class PrototypeTests(unittest.TestCase):
    def setUp(self):
        self.content = HTML.read_text(encoding="utf-8")
        self.doc = SiteParser()
        self.doc.feed(self.content)
    def test_accessibility_and_private_prototype_markers(self):
        self.assertEqual(self.doc.lang, "pt-BR")
        self.assertEqual(self.doc.robots, "noindex,nofollow")
        self.assertIn("NÃO PUBLICADO", self.content)
        self.assertIn('aria-label="Navegação do conteúdo"', self.content)
    def test_internal_navigation_targets_exist(self):
        self.assertGreaterEqual(len(self.doc.links), 5)
        for link in self.doc.links:
            self.assertTrue(link.startswith("#"), link)
            self.assertIn(link[1:], self.doc.ids)
    def test_content_is_explicitly_demonstrative(self):
        self.assertIn("demonstracao_nao_publicada", self.content)
        self.assertIn("não representa participação real", self.content)
        self.assertIn("ainda não reconciliado", self.content)

if __name__ == "__main__":
    unittest.main()
