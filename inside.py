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

def quote_nodes(sents):
    nodes = []
    for sent in sents:
        quotes = get_quotes(sent)
        
        #assumes that the number of closing quotes is less than the number of opening
        #loops for length of opening and closing quotes, appending each node between them
        for num in range(len(quotes[1])):
            for curr in range(quotes[0][num]+1, quotes[1][num]):
                nodes.append(sent[curr])
                
    return nodes

def get_question(sent):
    for node in sent:
        if node['governor'] == "?":
            return sent
    return None

def question_nodes(sents):
    nodes = []
    for sent in sents:
        question = get_question(sent)
        if question != None:
            nodes.extend(question)
    return nodes

def get_negs(sent):
    verb = None
    for node in sent:
        if node['relation'] == "neg":
            nodes = sisters.get_nodes(sent, node['governor'])[1]
            verb = node['governor']
    return (verb, nodes)

def negation_nodes(sents):
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
    
    tag = "neg"
    sentence = "John didn't realize there were cookies on the table."
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = negation_nodes(dependency)
    labels =  sisters.label(nodes[1], tag)
    for verb in nodes[0]:
        labels.append("neg_" + verb)
    print labels
    
