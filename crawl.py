#!/usr/bin/env python

from urlparse import urljoin

from lxml.html import parse, tostring

def crawl():
    for url in bisac_pages():
        for term in terms(url):
            print term

def terms(url):
    doc = parse(url)
    for tr in doc.findall('.//div[@class="detail"]//tr'):
        cells = tr.findall('td')
        if len(cells) != 2: continue

        notation, label = cells
        if notation.text == None:
            alt = format_label(label.text)
            divider = label.find('i')
            if divider == None:
                divider = label.find('em')
            if divider.tail == None:
                continue
            pref = format_label(divider.tail)
            yield 'alt_label', pref, alt
        else:
            pref_label = format_label(label.text)
            yield 'concept', notation.text, format_label(label.text)

def bisac_pages():
    url = "http://www.bisg.org/what-we-do-0-136-bisac-subject-headings-list-major-subjects.php"
    doc = parse(url)
    for a in doc.xpath('.//ul[@class="list"]/li/a'):
        yield urljoin(url, a.attrib['href'])

def format_label(s):
    s = s.lower().strip()
    parts = s.split(' ')
    parts = [p.capitalize() for p in parts]
    return ' '.join(parts)

if __name__ == "__main__":
    crawl()
