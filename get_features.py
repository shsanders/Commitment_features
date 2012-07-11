'''
Created on Jul 6, 2012

@author: random
'''

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

def get_oppose(first, second, oppose, deps, pos):
    to_return = []
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are opposed
    for word in first:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'you':
            to_return.append(nodes)
    for word in second:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'i':
            to_return.append(nodes)
    for word in oppose:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'you' or nodes[1]['dependent'].lower() == 'i':
            to_return.append(nodes)   
    
    return to_return

def get_commit(commit, first, second, deps, pos):
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are committed
    to_return = []
    for word in first:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'i':
            to_return.append(nodes)
    for word in second:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'you':
            to_return.append(nodes)
    for word in commit:
        nodes = sisters.get_nodes(deps, word)
        if nodes[1]['dependent'].lower() == 'you' or nodes[1]['dependent'].lower() == 'i':
            to_return.append(nodes)
            
    return to_return

def update_feat_vect():
    regardless_commit, first_commit, second_commit, regardless_oppose = load_words()
    oppose = get_oppose(first_commit, second_commit, regardless_oppose)
    commit = get_commit(regardless_commit, first_commit, second_commit)
    print "regardless_commit: ", regardless_commit
    print "first_commit: ", first_commit
    print "second_commit: ", second_commit
    print "regardless_oppose: ", regardless_oppose
        

import idioms_adverbs
import inside
import sisters
to_open = range(1000)

update_feat_vect()

            
    