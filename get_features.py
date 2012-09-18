'''
Created on Jul 6, 2012

@author: random
'''

from nlp import boundary
import listTree
import sisters

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
def get_oppose(first, second, oppose, tree):
    to_return = []
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are opposed
    for word in first:
        ##Finds nodes that are complements of first-person commit
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'you':
                to_return.append((word, nodes[1]))
    for word in second:
        ##Of second person commmit
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'i':
                to_return.append((word, nodes[1]))
    for word in oppose:
        ##Of either oppose
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'you' or nodes[0].word.lower() == 'i':
                to_return.append((word, nodes[1])) 
    return to_return  
    
def get_commit(commit, first, second, tree):
    ##Go through each set of verbs and pull out its dependents
    ##Keep those lists that are committed
    ##Exactly like get_oppose, just swapped you and i and changed to commit regardless
    to_return = []
    for word in first:
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'i':
                to_return.append((word, nodes[1]))
    for word in second:
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'you':
                to_return.append((word, nodes[1]))
    for word in commit:
        nodes = sisters.get_nodes(word, tree)
        if (nodes[0] != None):
            if nodes[0].word.lower() == 'you' or nodes[0].word.lower() == 'i':
                to_return.append((word, nodes[1]))            
    return to_return

def update_feat_vect(tree, word_lists):
    ##Load word lists
    regardless_commit, first_commit, second_commit, regardless_oppose = word_lists
    ##Get oppose words and nodes
    oppose = get_oppose(first_commit, second_commit, regardless_oppose, tree)
    ##Get commit words and nodes
    commit = get_commit(regardless_commit, first_commit, second_commit, tree)
    ##Return tuple consisting of (commit tuples, oppose tuples)
    return (commit, oppose)
##The final data structure goes ( [ (commit word, [commit nodes]) ...], [ (oppose word, [oppose nodes]) ] )

def update(name, node, vect):
    '''
    vect[name+"unigram: "+node.word.lower()] += 1
    if node.liwc != None:
        for key in dict(node.liwc):
            vect[name+"LIWC: "+key] += 1
    '''        
                
    if node.deps != None:
        for curr in node.deps:
            dep_string = "pos_genDep: %s(%s,%s)" % (curr.rel, node.pos, curr.lemma)
            dep_string = name + dep_string
            vect[dep_string] += 1
    
    '''
    if node.mpqa != None:
        pass
        ##this needs to be filled with the appropriate mpqa feature stuff
    '''
        
def build_ranges(nodes, name, is_quote=False):
    starts = [node for node in nodes]
    quote_types = ["'", "''", "`", "``"]
    to_return = []
    found_nodes = []
    start = None
    prev = None
    for node in nodes:
        if start == None:
            #if there's no node starting the range, use this one
            start = node
        else:
            #if there is a start node, it's either prev or connected to prev
            #via function words. take prev and see if it connects to node via
            #a series of function words or directly
            curr = prev
            if curr.nxt != node:
                if curr.nxt != None:
                    curr = curr.nxt
                    #make a list to add function words to
                    to_extend = []
                    while curr.gov == None and curr.deps == None:
                        if is_quote and (curr.lemma in quote_types):
                            break
                        #add the function word
                        to_extend.append(curr)
                        #go to the next word
                        if curr.nxt != None:
                            curr = curr.nxt
                        else:
                            if curr.next_tree != None:
                                curr = curr.next_tree
                            else:
                                break
                    if curr != node:
                        #if it didn't find a connection between prev and node,
                        #store the old range and start a new one
                        to_return.append((start.start, prev.end, name))
                        start = node
                    else:
                        #if it did find a range, extend nodes with the function words
                        found_nodes.extend(to_extend)
                else:
                    to_return.append((start.start, curr.end, name))
                    start = node
        #change prev
        prev = node
    if prev != None:
        if start == None:
            start = prev
        to_return.append((start.start, prev.end, name))
    starts.extend([node for node in found_nodes])
    return (to_return, starts, found_nodes)
    
def feat_vect(deps, pos, vect):
    trees = listTree.build_ListTrees(deps, pos)
    nones = []
    tuples = []
    quotes = []
    questions = []
    antecedents = []
    consequents = []
    neg_verbs = []
    neg_all = []
    commit_starts = []
    for num in range(len(trees)):
        tree = trees[num]
        '''
        verbs, all_neg = tree.get_neg()
        if verbs:
            neg_verbs.extend(verbs)
            verbs = sorted(list(set(verbs)), key=lambda node: node.start)
            ranged = build_ranges(verbs, 'neg_verbs')
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            neg_verbs.extend(ranged[2])
        if all_neg:
            neg_all.extend(all_neg)
            all_neg = sorted(list(set(all_neg)), key=lambda node: node.start)
            ranged = build_ranges(all_neg, 'neg_all')
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            neg_all.extend(ranged[2])
        '''    
        question = tree.get_question()
        if question != None:
            questions.extend(question)
            question = sorted(list(set(question)), key=lambda node: node.start)
            ranged = build_ranges(question, 'question')
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            questions.extend(ranged[2])
            for node in question:
                node.commitment = True

        condit = tree.get_cond()
        if condit[0] != None and condit[1] != None:            
            ant, cons = condit
            antecedents.extend(ant)
            ant = sorted(list(set(ant)), key=lambda node: node.start)
            ranged = build_ranges(ant, 'antecedent')
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            antecedents.extend(ranged[2])
            for node in ant:
                node.commitment = True
            
            consequents.extend(cons)
            cons = sorted(list(set(cons)), key=lambda node: node.start)
            ranged = build_ranges(cons, 'consequent')
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            antecedents.extend(ranged[2])
            for node in cons:
                node.commitment = True

            
    if len(trees) > 0:
        quotes = trees[0].get_quotes()
        if len(quotes) > 0:
            quotes= sorted(list(set(quotes)), key=lambda node: node.start)
            ranged = build_ranges(quotes, 'quote', is_quote=True)
            tuples.extend(ranged[0])
            commit_starts.extend(ranged[1])
            quotes.extend(ranged[2])
            for node in quotes:
                node.commitment = True
                
    for tree in trees:
        curr = tree.start
        while curr != None:
            nones.append(curr)
            curr = curr.nxt
    commits = quotes + questions + antecedents + consequents + neg_all + neg_verbs
    nones = [node for node in nones if node not in commits]
            
    nones = sorted(list(set(nones)), key=lambda node: node.start)
    ranged = build_ranges(nones, 'none')
    tuples.extend(ranged[0])
    nones.extend(ranged[2])
    

    name = "NONE_"
    for node in nones:
        update(name, node, vect)
    
    name = "QUOTE_"
    for node in quotes:
        update(name, node, vect)
        
    name = "QUESTION_"
    for node in questions:
        update(name, node, vect)
    
    name = "ANTECEDENT_"
    for node in antecedents:
        update(name, node, vect)
        
    name = "CONSEQUENT_"
    for node in consequents:
        update(name, node, vect)
    '''    
    name = "NEG_VERBS_"
    for node in neg_verbs:
        update(name, node, vect)
        
    name = "NEG_ALL_"
    for node in neg_all:
        update(name, node, vect)
    '''    
        
    return tuples

if __name__ == '__main__':
    
    

    import json
    
    curr_file = "/home/random/workspace/Persuasion/data/convinceme/output_by_thread/1736/21585.json"
    j = json.load(open(curr_file))
    pos = j[0]
    deps = j[2]
    
    trees = listTree.build_ListTrees(deps, pos)
    
    for tree in trees:
        print tree
        
    quotes = trees[0].get_quotes()
    print
    print
    print quotes
    print 
    print
    vect = {}
    tuples = feat_vect(deps, pos, vect)
    if len(vect) > 0:
        print vect
        
    for tup in tuples:
        print tup
