#!/usr/bin/env python

import re
import json
import logging

from urlparse import urljoin

from lxml import html

def concepts():
    """Crawls all the BISAC pages.
    """
    concepts = {}
    alt_labels = {}
    relateds = {}
    for url in urls():
        logging.info("parsing %s", url)
        results = assemble(url)
        concepts.update(results[0])
        alt_labels.update(results[1])
        relateds.update(results[2])

    # now that we have all of the concepts we can add the alt labels
    for pref_label in alt_labels.keys(): 
        if concepts.has_key(pref_label):
            concepts[pref_label]['alt_label'] = alt_labels[pref_label]
        else:
            logging.warn("missing pref label in alt_labels: %s", pref_label)

    # and related labels
    for pref_label in relateds.keys():
        if concepts.has_key(pref_label):
            for related in relateds[pref_label]:
                concepts[pref_label]['related'].append(related)
        else:
            logging.warn("missing pref label in relateds: %s", pref_label)

    open("bisac.json", "w").write(json.dumps(concepts, indent=2))

def assemble(url):
    concepts = {}
    alt_labels = {}
    relateds = {}
    for term in parse(url):
        logging.info("got term: %s", term)
        term_type = term.pop(0)
        if term_type == "CONCEPT":
            notation, pref_label = term
            concepts[pref_label] = {"notation": notation,
                                    "pref_label": pref_label,
                                    "alt_label": [],
                                    "related": []}
        elif term_type == "ALT_LABEL":
            alt_label = term.pop(0)
            for pref_label in term:
                add(alt_labels, pref_label, alt_label)
        elif term_type == "RELATED":
            pref_label = term.pop(0)
            for related in term:
                add(relateds, pref_label, related)

    return concepts, alt_labels, relateds

def add(d, k, v):
    if d.has_key(k):
        d[k].append(v)
    else:
        d[k] = [v]

def parse(url):
    """A generator that returns concepts and alt labels as terms from 
    a BISAC web page.
    """
    doc = html.parse(url)
    for tr in doc.findall('.//div[@class="detail"]//tr'):
        logging.info("got <tr>: %s", html.tostring(tr))
        cells = tr.findall('td')
        if len(cells) != 2: continue

        notation = cells[0].text
        labels = extract_labels(cells[1])

        if not notation:
            for see_also in labels[1:]:
                yield ['ALT_LABEL', labels[0], see_also]
        elif notation and len(labels) == 1:
            yield ['CONCEPT', notation, labels[0]]
        elif notation and len(labels) > 1:
            for related in labels[1:]:
                yield['RELATED', labels[0], related]
        else:
            logging.error("unknown term type")

def urls():
    url = "http://www.bisg.org/what-we-do-0-136-bisac-subject-headings-list-major-subjects.php"
    doc = html.parse(url)
    for a in doc.xpath('.//ul[@class="list"]/li/a'):
        yield urljoin(url, a.attrib['href'])

def format_label(s):
    s = s.lower().strip().strip(' *').strip(')')
    parts = s.split(' ')
    parts = [p.capitalize() for p in parts]
    return ' '.join(parts)

def extract_labels(e):
    """the kinda nasty bit that unpacks:
    
    <td>ANTIQUES & COLLECTIBLES / Hummels <i>see</i> Figurines <i>or</i> Popular Culture</td>"

    into:

    ["Antiques & Collectibles / Hummels", "Antiques & Collectibles / Figurines", "Antiques & Collectibles / Popular Culture"]
    """
    from_label = format_label(e.text)
    main = hierarchy(from_label)[0]

    chain = [from_label]
    for p in e:
        if p.tail == None:
            continue
        see_label = format_label(p.tail)
        if not re.match('^[A-Z]+ /.*$', p.tail):
            see_label = " / ".join([main, see_label])
        chain.append(see_label)
    return chain

def hierarchy(text):
    return text.split(" / ")

if __name__ == "__main__":
    logging.basicConfig(filename="bisac.log", level=logging.INFO)
    concepts()
