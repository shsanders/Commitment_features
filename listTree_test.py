'''
Created on Jul 24, 2012

Simple script for test listTree
Parses a sentence, builds a ListTree, prints that bitch

One issue with the test sentence - "cookies" gets indexed as 0 for some reason,
so the ListTree puts it in front of everything else and prints it out that way.

@author: random
'''

from nlp.stanford_nlp import get_parses

import listTree

sent = "I admit that I like cookies"

print sent

parse = get_parses(sent)

trees = listTree.build_ListTrees(parse[2])

for tree in trees:
    print tree