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

##Both get_commit and get_oppose return a list of tuples
##Each tuple goes (context word, [list of nodes that are complements of context word])


##First, second, oppose, commit are all lists of words
##Dep is a single dependency graph, pos is a single pos list for a sentence
def get_oppose(first, second, oppose, dep, pos):
    to_return = []
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are opposed
    for word in first:
        ##Finds nodes that are complements of first-person commit
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you':
                to_return.append((word, nodes[1]))
    for word in second:
        ##Of second person commmit
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1]))
    for word in oppose:
        ##Of either oppose
        nodes = sisters.get_nodes(dep, word)
        if (nodes[0] != None):
            if nodes[0]['dependent'].lower() == 'you' or nodes[0]['dependent'].lower() == 'i':
                to_return.append((word, nodes[1])) 
    return to_return  
    
def get_commit(commit, first, second, dep, pos):
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are committed
    ##Exactly like get_oppose, just swapped you and i and changed to commit regardless
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
    ##Load word lists
    regardless_commit, first_commit, second_commit, regardless_oppose = load_words()
    ##Get oppose words and nodes
    oppose = get_oppose(first_commit, second_commit, regardless_oppose, dep, pos)
    ##Get commit words and nodes
    commit = get_commit(regardless_commit, first_commit, second_commit, dep, pos)
    ##Return tuple consisting of (commit tuples, oppose tuples)
    return (commit, oppose)
##The final data structure goes ( [ (commit word, [commit nodes]) ...], [ (oppose word, [oppose nodes]) ] )


import idioms_adverbs
import inside
import sisters
import json

to_open = range(50)


commits = []
opposes = []


##This is all just a test load and parse
for num in to_open:
    curr_file = "/home/random/workspace/sarcasm/instances/" + str(num) + ".json"
    j = json.load(open(curr_file))
    text = j['response_text']
    pos = j['response_pos']
    deps = j['response_dep']
    for num in range(len(deps)):
        tups = update_feat_vect(deps[num], pos[num])
        ##tup[0] = commit tuples, tup[1] = oppose tuples
        for tup in tups[0]:
            if len(tup) > 0:
                print text
                print "Commit CURR_WORD: ", tup[0]
                for node in tup[1]:
                    print node['dependent']
                print
        
        for tup in tups[1]:
            if len(tup) > 0:
                print text
                print "Oppose CURR_WORD: ", tup[0]
                for node in tup[1]:
                    print node['dependent']
                print