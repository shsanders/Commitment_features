from nlp import stanford_nlp 

def get_roots(dependencies, word):
    """gather all the nodes that meet the requirement"""
    subroots = set()
    try:
        possible = [dependency['dependent_index'] for dependency in dependencies if dependency['governor'].startswith(word)]
        subroots.update(possible)
    except Exception, e:
        print 'Exception:{}'.format(e)
    def _roots(dependencies, word):
        """recursive helper function for gathering the nodes"""
        for dependency in dependencies:
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
            #you can play around with what you want to store here, currently it just stores the dependent word
            #alternatively you could store the entire dependency so that you could look at different elements at
            #a later time
    return deps

def get_children_dependency(sentence, word):
    results = []
    result = match(sentence, word)
    results.extend(result)
    return results

def get_nodes(sentence, word, strip=False):
    nodes = get_children_dependency(sentence, word)
    subj = None
    for node in nodes:
        if node['relation'] == "nsubj":
            subj = node
            nodes.remove(node)
            break
    if strip:
        for node in nodes:
            if node['relation'] == "mark" or node['relation'] == "complm":
                nodes.remove(node)
    return(subj, nodes)    
    
def label(deps, tag):
    return ["{}_{}".format(tag, dep['dependent']) for dep in deps]

if __name__ == '__main__':
    tag = "agree"
    sentence = 'I agree with Bob about how ugly Steve is.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)

    sentence = 'I am not sure if Steve agrees with Bob.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)

    sentence = 'I agree that people are stupid. You agree they are nice.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    for sent in dependency:
        nodes = get_nodes(sent, tag)
        print label(nodes[1], tag)

    tag = "admit"
    sentence = 'I admit that I like cookies.'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    
    sentence = 'I admit that I like cookies'
    print sentence
    pos,meta,dependency = stanford_nlp.get_parses(sentence)
    nodes = get_nodes(dependency[0], tag)
    print label(nodes[1], tag)
    

    #additionally you can pass the dep tree from the jsons into the get_children_dependency(dep_tree, 'search_word')
