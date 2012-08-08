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
    vect[name+node.lemma] = True
    if node.liwc != None:
        for key in dict(node.liwc):
            if name+"LIWC: "+key in vect:
                vect[name+"LIWC: "+key] += 1
            else:
                vect[name+"LIWC: "+key] = 1
                
    if node.deps != None:
        for curr in node.deps:
            dep_string = "%s(%s,%s)" % (curr.rel, node.lemma, curr.lemma)
            dep_string = name + dep_string
            if dep_string in vect:
                vect[dep_string] += 1
            else:
                vect[dep_string] = 1
    if node.mpqa != None:
        pass
        ##this needs to be filled with the appropriate mpqa feature stuff
        
def build_ranges(nodes, name):
    to_return = []
    start = None
    prev = None
    for node in nodes:
        if start == None:
            start = node.start
        else:
            curr = prev
            if curr.nxt != node:
                while not curr.pos.isalpha():
                    if curr.nxt != None:
                        curr = curr.nxt
                    else:
                        break
                if curr != node:
                    to_return.append((start, prev.end, name))
                    start = None
        prev = node
    if start == None:
        start = prev.start
    to_return.append((start, prev.end, name))
    return to_return
    
def feat_vect(deps, pos, vect):
    trees = listTree.build_ListTrees(deps, pos)
    environs = 0
    quotes = []
    questions = []
    antecedents = []
    conditionals = []
    tuples = []
    for tree in trees:
        quote = tree.get_quotes()
        if quote != None:
            quotes.extend(quote)
            environs += 1
            sort_quote = sorted(list(set(quote)), key=lambda node: node.index)
            tuples.extend(build_ranges(sort_quote, 'quote'))
            for tup in build_ranges(sort_quote, "quote"):
                pass
        question = tree.get_question()
        if question != None:
            questions.extend(question)
            environs += 1
            sort = sorted(list(set(question)), key=lambda node: node.index)
            tuples.extend(build_ranges(sort, 'question'))
            for tup in build_ranges(sort, "question"):
                pass
        condit = tree.get_cond()
        if condit[0] != None and condit[1]:
            ant, cond = condit
            antecedents.extend(ant)
            sort = sorted(list(set(ant)), key=lambda node: node.index)
            tuples.extend(build_ranges(sort, 'antecedent'))
            for tup in build_ranges(sort, "antecedent"):
                pass
            conditionals.extend(cond)
            sort = sorted(list(set(cond)), key=lambda node: node.index)
            tuples.extend(build_ranges(sort, 'conditional'))
            for tup in build_ranges(sort, "conditional"):
                pass
            environs += 1
    
    name = "quote: "
    for node in quotes:
        update(name, node, vect)
        
    name = "question: "
    for node in questions:
        update(name, node, vect)
        
    name = "antecedent: "
    for node in antecedents:
        update(name, node, vect)
        
    name = "conditional: "
    for node in conditionals:
        update(name, node, vect)

    return tuples

if __name__ == '__main__':
    
    import json

    to_open = range(7)


    word_lists = load_words()
    ##This is all just a test load and parse
    for num in to_open:
        vect = {}
        curr_file = "/home/random/workspace/Utilities/nlp/output_by_thread/1/790" + str(num) + ".json"
        j = json.load(open(curr_file))
        pos = j[0]
        deps = j[2]
        feat_vect(deps, pos, vect)
        if len(vect) > 0:
            print vect
