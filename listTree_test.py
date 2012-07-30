'''
Created on Jul 24, 2012

Simple script for test listTree
Parses a sentence, builds a ListTree, prints that bitch

One issue with the test sentence - "cookies" gets indexed as 0 for some reason,
so the ListTree puts it in front of everything else and prints it out that way.

@author: random
'''

def print_node_rels(node, seen):
    to_return = ""
    if node != None:
        to_return += "Node: " + str(node)
        if node not in seen:
            seen.append(node)
            to_return += " Gov: " + print_node_rels(node.gov, seen)
            to_return += " Deps: "
            if node.deps != None:
                for dep in node.deps:
                    to_return += print_node_rels(dep, seen) + " "
    return to_return
            
    

from nlp.stanford_nlp import get_parses

import listTree

sent = "I admit that I like cookies."

print sent

parse = get_parses(sent)

print parse[2]

trees = listTree.build_ListTrees(parse[2])

for tree in trees:
    print tree
    curr = tree.start
    print "Start: ", tree.start
    while (curr != None):
        print "Curr: " + str(curr)
        print " gov: " + str(curr.gov) 
        print " deps: "
        if curr.deps != None:
            for dep in curr.deps:
                print dep
        curr = curr.nxt