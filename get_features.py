'''
Created on Jul 6, 2012

@author: random
'''

from nlp import boundary

def load_words():
    ##Function that loads four sets of verbs to check the sisters of
    ##List of the files to load from
    to_load = ["regardless_commit.txt", "first_commit.txt", "second_commit.txt", "regardless_oppose.txt"]
    words = []
    for name in to_load:
        ##Open each file, load the words from that file
        curr_file = open(name, 'r')
        curr_list = []
        while (True):
            token = curr_file.readline()
            if token == "":
                break
            token = token.rstrip("\n")
            if token != "":
                curr_list.append(token)
        words.append(curr_list)
    return words

def get_oppose(first, second, oppose, dep, pos):
    to_return = []
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are opposed
    for word in first:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you':
                to_return.append((word, nodes[1]))
    for word in second:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1]))
    for word in oppose:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you' or nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1])) 
    return to_return  
    
def get_commit(commit, first, second, dep, pos):
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are committed
    to_return = []
    for word in first:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1]))
    for word in second:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you':
                to_return.append((word, nodes[1]))
    for word in commit:
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you' or nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1]))            
    return to_return

def update_feat_vect(dep, pos):
    regardless_commit, first_commit, second_commit, regardless_oppose = load_words()
    oppose = get_oppose(first_commit, second_commit, regardless_oppose, dep, pos)
    commit = get_commit(regardless_commit, first_commit, second_commit, dep, pos)
    return (commit, oppose)


import idioms_adverbs
import inside
import sisters
import json

to_open = range(50)


commits = []
opposes = []

for num in to_open:
    curr_file = "/home/random/workspace/sarcasm/instances/" + str(num) + ".json"
    j = json.load(open(curr_file))
    pos = j['response_pos']
    deps = j['response_dep']
    for num in range(len(deps)):
        tup = update_feat_vect(deps[num], pos[num])
        if len(tup[0]) > 0: 
            commits.append(tup[0])
        if len(tup[1]) > 0:
            opposes.append(tup[1])

for commit in commits:
    print commit[0][0]
    for dep in commit[0][1]:
        print dep['dependent_index']
print opposes
    