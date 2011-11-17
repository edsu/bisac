import logging

from unittest import TestCase, main

from lxml import html

import bisac 

class BisacTests(TestCase):
    
    def test_urls(self):
        urls = list(bisac.urls())
        self.assertEqual(len(urls), 51)
        self.assertEqual(urls[0], "http://www.bisg.org/what-we-do-0-85-bisac-subject-headings-list-antiques-and-collectibles.php")

    def test_parse(self):
        url = "http://www.bisg.org/what-we-do-0-85-bisac-subject-headings-list-antiques-and-collectibles.php"
        terms = list(bisac.parse(url))
        self.assertEqual(len(terms), 73)

    def test_assemble(self):
        url = "http://www.bisg.org/what-we-do-0-85-bisac-subject-headings-list-antiques-and-collectibles.php"
        concepts, alt_labels = bisac.assemble(url)

    def test_extract_labels(self):
        e = html.fromstring("<td>ANTIQUES & COLLECTIBLES / Hummels <i>see</i> Figurines <i>or</i> Popular Culture</td>")
        expected = ["Antiques & Collectibles / Hummels", "Antiques & Collectibles / Figurines", "Antiques & Collectibles / Popular Culture"]
        self.assertEqual(bisac.extract_labels(e), expected)

if __name__ == "__main__":
    logging.basicConfig(filename="test.log", level=logging.DEBUG)
    main()
