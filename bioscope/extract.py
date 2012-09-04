#!/usr/bin/env python
import json
import xml.etree.ElementTree as ElementTree
from collections import defaultdict

TOKEN = 'token'
SPAN = 'span'

def extract(dumpfile='dump.json'):
    keywords = defaultdict(lambda: defaultdict(list))
    for filename in ['abstracts.xml', 'full_papers.xml']:
        tree = ElementTree.parse(filename)
        root = tree.getroot()
        for child in root.iter('cue'):
            try:
                _type = child.attrib['type']
                keyword = child.text.lower()
                if ' ' in keyword:
                    slot = keywords[_type][SPAN]
                    if keyword not in slot:
                        slot.append(keyword)
                else:
                    slot = keywords[_type][TOKEN]
                    if keyword not in slot:
                        slot.append(keyword)
            except KeyError, e: continue
    with open(dumpfile, 'wb') as f:
        json.dump(keywords, f)

def main():
    extract(dumpfile='spec_neg_keywords.json')

if __name__ == '__main__':
    main()
