'''
Created on Jul 6, 2012

@author: random
'''

import idioms_adverbs
import inside
import sisters
import json

commits = ['agree', 'admit', 'advocate', 'afraid', 'argue', 'believe', 'claim', 'choose']

to_open = range(1000)

commitments = open("/home/random/polite_sents.txt", "w")

for num in to_open:
    curr_file = "/home/random/workspace/sarcasm/instances/" + str(num) + ".json"
    j = json.load(open(curr_file))
    deps = j['response_dep']
    text = j['response_text']
    for dep in deps:
        for commit in commits:
            commit_nodes = sisters.get_nodes(dep, commit)
            if len(commit_nodes[1]) > 0:
                print text
                print sisters.label(commit_nodes[1], commit)
            
    