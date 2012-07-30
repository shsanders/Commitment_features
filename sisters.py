from nlp import stanford_nlp 

def get_roots(dependencies, word):
    """gather all the nodes that meet the requirement"""
    subroots = set()
    visited = set()
    try:
        possible = [dependency['dependent_index'] for dependency in dependencies if dependency['governor'].startswith(word)]
        subroots.update(possible)
    except Exception, e:
        print 'Exception:{}'.format(e)
    def _roots(dependencies, word):
        """recursive helper function for gathering the nodes"""
        for dependency in dependencies:
            if dependency['dependent_index'] in visited: continue
            visited.add(dependency['dependent_index'])
            if dependency['governor'].startswith(word):
                if not dependency['dependent_index'] in subroots:
                    subroots.add(dependency['dependent_index'])
                subroots.update(_roots(dependencies, word=dependency['dependent']))
        return subroots
    return _roots(dependencies, word)
        
def match(dependencies, word):
    roots = get_roots(dependencies, word) 
    deps = []
    for dependency in dependencies:
        if dependency['dependent_index'] in roots:
            deps.append(dependency)
            #currently stores the whole node so that it's more robust
    return deps

def get_nodes(word, tree, strip=False):
    ##get a list of nodes governed by word
    nodes = tree.search_and_descend(word)
    subj = None
    for node in nodes:
        ##look for the first subj, then move it out of the list
        if node.rel == "nsubj" and node.gov.word == word:
            subj = node
            nodes.remove(node)
            break
    if strip:
        ##strip possibility because i think there might be issues with spurious
        ##words getting saved
        for node in nodes:
            if node.rel == "mark" or node.rel == "complm":
                nodes.remove(node)
    return(subj, nodes)
    
def label(deps, tag):
    return ["{}_{}".format(tag, dep['dependent']) for dep in deps]
    ##this function might be pointless now, but we should keep it just in case

if __name__ == '__main__':
    ##testing shit, can be deleted
    tag = "agree"
    sentence = 'I agree with Bob about how ugly Steve is.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    print nodes[0]

    sentence = 'I am not sure if Steve agrees with Bob.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    print nodes[0]

    sentence = 'I agree that people are stupid. You agree they are nice.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    for sent in dependency:
        nodes = get_nodes(sent, tag)
        print label(nodes[1], tag)
        print nodes[0]

    tag = "admit"
    sentence = 'I admit that I like cookies.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    print nodes[0]
    
    sentence = 'I admit that I like cookies'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    print nodes[0]
    

    #additionally you can pass the dep tree from the jsons into the get_children_dependency(dep_tree, 'search_word')
