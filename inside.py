'''
Created on Jun 26, 2012

@author: random
'''

import sisters
from nlp import stanford_nlp

def get_quotes(sent):
    open_quotes = []
    close_quotes = []
    
    ##build a set of opening and closing quotes
    for pos in sent:
        if pos['PartOfSpeech'] == "\'\'":
            close_quotes.append(int(pos['BeginIndex']))
        elif pos['PartOfSpeech'] == "``":
            open_quotes.append(int(pos['BeginIndex']))
    
    return (open_quotes, close_quotes)

def quote_nodes(sents, deps):
    nodes = []
    for i in range(len(deps)):
        dep = deps[i]
        sent = sents[i]
        indices = []
        quotes = get_quotes(sent)        
        #assumes that the number of closing quotes is less than the number of opening
        #loops for length of opening and closing quotes, appending each node between them
        for num in range(len(quotes[1])):
            for curr in range(quotes[0][num]+1, quotes[1][num]):
                indices.append(int(sent[curr]['TokenBegin']))
        print indices
        for edge in dep:
            if edge['dependent_index'] in indices:
                nodes.append(edge)
    return nodes

def get_question(sent): 
    ##just looks to see if there's a question mark, and returns the whole
    ##sentence's dependency parse if there is
    for node in sent:
        if node['governor'] == "?":
            return sent
    return None

def question_nodes(sents):
    ##goes through a set of dependencies and builds a full set of nodes
    ##from question sentences. might be pointless.
    nodes = []
    for sent in sents:
        question = get_question(sent)
        if question != None:
            nodes.extend(question)
    return nodes

def get_negs(sent):
    ##looks for a negation node, then gets all nodes governed by its governor
    ##which is, presumably, the main verb or the negated verb
    verb = None
    for node in sent:
        if node['relation'] == "neg":
            nodes = sisters.get_nodes(sent, node['governor'])[1]
            verb = node['governor']
    return (verb, nodes)

def negation_nodes(sents):
    ##builds a list of negated verbs and nodes by iterating
    ##over a list of dependencies
    nodes = []
    verbs = []
    for sent in sents:
        negs = get_negs(sent)
        nodes.extend(negs[1])
        verbs.append(negs[0])
    nodes = [node for node in nodes if node['relation'] != "neg"]
    #the verbs and the nodes need to be treated differently, nodes are nodes, verbs are strings
    return (verbs, nodes)

if __name__ == '__main__':
    tag = "?"
    sentence = '"Life threatening condition that is always physically harmful"? What a giant load of steamy BS.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = question_nodes(dependency)
    print sisters.label(nodes, tag)

    
    tag = "quote"
    sentence = '"Life threatening condition that is always physically harmful"? What a giant load of steamy BS.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    words = quote_nodes(pos, dependency)
    print sisters.label(words, tag)
    
    tag = "quote"
    sentence = "John said 'I like cookies.'"
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    words = quote_nodes(pos, dependency)
    print sisters.label(words, tag)
