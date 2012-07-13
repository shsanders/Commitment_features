import sisters
from nlp import stanford_nlp

def get_adv(sent, adv):
    ##takes in an adverb, finds it in the dependency, pulls out everything
    ##it governs
    verb = None
    for node in sent:
        if node['dependent'] == adv:
            nodes = sisters.get_nodes(sent, node['governor'])[1]
            verb = node['governor']
    return (verb, nodes)

def get_adv_nodes(sents, adv):
    ##does get_adv for a set of dependencies, builds a verb and node list
    nodes = []
    verbs = []
    for sent in sents:
        advs = get_adv(sent, adv)
        nodes.extend(advs[1])
        verbs.append(advs[0])
    nodes = [node for node in nodes if node['dependent'] != adv]
    #the verbs and the nodes need to be treated differently, nodes are nodes, verbs are strings
    return (verbs, nodes)

def get_idiom(sent, gov_dep):
    ##takes a tuple/list consisting of a two-part idiom, the first one should
    ##be the word that governs the other. this could maybe be changed so it
    ##could be a list of any size
    nodes = None
    for node in sent:
        ##finds two nodes with the appropriate relation, pulls everything they
        ##govern, and returns that list
        if node['dependent'].lower() == gov_dep[1] and node['governor'].lower() == gov_dep[0]:
            nodes = sisters.get_nodes(sent, node['governor'])[1]
    return [node for node in nodes if node['dependent'].lower() not in gov_dep]
    

def idiom_nodes(sents, gov_dep):
    ##does get_idioms for all dependencies in a listS
    nodes = []
    for sent in sents:
        idioms = get_idiom(sent, gov_dep)
        nodes.extend(idioms)
    return nodes

if __name__ == '__main__':
    tag = "really"
    sentence = "I really like cookies."
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_adv_nodes(dependency, tag)
    labels =  sisters.label(nodes[1], tag)
    for verb in nodes[0]:
        labels.append("really_" + verb)
    print labels
    
    tag = "would_say"
    sentence = "I would say cookies are delicious."
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = idiom_nodes(dependency, ["say", "would"])
    labels =  sisters.label(nodes, tag)
    print labels
    
    tag = "it_appears"
    sentence = "It appears cookies are delicious."
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = idiom_nodes(dependency, ["appears", "it"])
    labels =  sisters.label(nodes, tag)
    print labels