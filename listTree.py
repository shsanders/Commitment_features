'''
Created on Jul 19, 2012

ListTree class fully functional. Build a new list of 
ListTrees by calling the function build_ListTrees on a list of semantic
dependencies. Each dependency graph will be turned into its own tree.

@author: random
'''

import mpqa.mpqa as mpqa

from nlp.word_category_counter import score_word


class Node:
    '''
    Node class for ListTree
    Nodes are connected in governor-relation manner and in
    linear first-last sentence order
    each node contains info about that word
    nxt = next, prev = previous, gov = governor, deps = list of dependents
    everything else is information about the word
    '''

    def __init__(self, word, index, pos, rel=None, lemma=None, start=None, end=None):
        '''
        constructor
        '''
        self.next_tree = None
        self.gov = None
        self.deps = None
        self.prev = None
        self.nxt = None
        self.dist = None
        self.start = start
        self.end = end
        self.mpqa = mpqa.lookup(word, pos)
        self.liwc = score_word(word)
        self.pos = pos
        self.word = word
        self.index = index
        self.rel = rel
        self.lemma = lemma
        
    def __repr__(self):
        ##Prints in the format 
        ##index: word, pos, rel, lemma
        ##gov:
        ##deps:
        ##mpqa:
        ##liwc
        ##prev:
        ##nxt:
        to_return = str(self.index) + ": " + self.word + ", " + self.pos + ", " + str(self.rel) + ", " 
        if self.lemma != None:
            to_return += str(self.lemma)
        to_return += "\ngov: "
        if self.gov != None:
            to_return += self.gov.word
        to_return += "\ndeps: "
        if self.deps != None:
            for node in self.deps:
                to_return += node.word + " "
        to_return += "\nrange: "
        if self.end != None:
            to_return += str(self.start)
        to_return += ", "
        if self.start != None:
            to_return += str(self.end)
        to_return += "\nprev: "
        if self.prev != None:
            to_return += self.prev.word
        to_return += "\n"
        to_return += "nxt: "
        if self.nxt != None:
            to_return += self.nxt.word
        return to_return
    
    def get_descendents(self, dist, notStart=True):
        if self.dist <= dist and notStart:
            return
        deps = []
        if self.deps != None:
            deps.extend(self.deps)
            for dep in self.deps:
                des = dep.get_descendents(self.dist)
                if des != None:
                    for node in des:
                        if node not in deps:
                            node.commitment = True
                            deps.append(node)
        return deps
    
    def top_ends(self):
        curr = self.gov
        found = []
        while (curr != None):
            if curr in found:
                return False
            found.append(curr)
            curr = curr.gov
        return True
    
    def build_dist(self, dist):
        ##Only call this on the root node, otherwise you will fuck
        ##everything up. Seriously. I'm not joking. Don't do it.
        if self.dist != None:
            return
        self.dist = dist
        dist += 1
        if self.deps != None:
            for dep in self.deps:
                dep.build_dist(dist)
        
class ListTree:
    '''
    start = first node in sentence order
    root = root node, top of the dependency tree
    end = last node in sentence order, useful for some things
    '''

    def __init__(self):
        '''
        Constructor, does nothing other than instantiate
        '''
        self.start = None
        self.root = None
        self.end = None
        
    def __repr__(self):
        ##Prints each word/node in sequential order according to the
        ##node string function
        to_return = ""
        trees = ""
        curr = self.start
        while (curr != None):
            to_return += str(curr.word) + " "
            trees += "\n" + str(curr)
            curr = curr.nxt
        ##to_return += trees
        return to_return
            

    def add_node(self, edge):
        ##Creates two nodes out of the edge
        nodeA = Node(edge['governor'], edge['governor_index'], edge['governor_pos'])
        nodeB = Node(edge['dependent'], edge['dependent_index'], edge['dependent_pos'], edge['relation'])
        
        curr = self.start
        
        if curr == None:
            ##If no nodes already in the ListTree, start at start
            nodeA.deps = [nodeB]
            nodeB.gov = nodeA
            nodeB.rel = edge['relation']
            if nodeA.index <= nodeB.index:
                self.start = nodeA
                self.end = nodeB
                nodeA.nxt = nodeB
                nodeB.prev = nodeA
            else:
                self.start = nodeB
                self.end = nodeA
                nodeB.nxt = nodeA
                nodeA.prev = nodeB
        else:
            ##Otherwise, go through each node starting at start and find the
            ##right place to insert the node
            prev = None 
            correctA = None
            while(curr != None and curr.index <= nodeA.index):
                if curr.index == nodeA.index:
                    correctA = curr
                    break
                prev = curr
                curr = curr.nxt
            ##Insert the node
            if correctA == None:
                nodeA.nxt = curr
                nodeA.prev = prev
                if prev != None:
                    prev.nxt = nodeA
                if curr != None:
                    curr.prev = nodeA
                if self.start == nodeA.nxt:
                    self.start = nodeA
                if self.end == nodeA.prev:
                    self.end = nodeA
            
            ##Do the same for the other node
            curr = self.start       
            prev = None 
            correctB = None
            while(curr != None and curr.index <= nodeB.index):
                if curr.index == nodeB.index:
                    correctB = curr
                    break
                prev = curr
                curr = curr.nxt
                
            if correctB == None:
                nodeB.nxt = curr
                nodeB.prev = prev
                if prev != None:
                    prev.nxt = nodeB
                if curr != None:
                    curr.prev = nodeB
                if self.start == nodeB.nxt:
                    self.start = nodeB
                if self.end == nodeB.prev:
                    self.end = nodeB
        
            ##Check to see if any node was already there
            ##Change the appropriate fields if either was already there
            if correctA != None:
                if correctB != None:
                    if correctA.deps == None:
                        correctA.deps = [correctB]
                    else:
                        if correctB not in correctA.deps:
                            correctA.deps.append(correctB)
                    correctB.gov = correctA
                    correctB.rel = edge['relation']
                    
                else:
                    nodeB.gov = correctA
                    nodeB.rel = edge['relation']
                    if correctA.deps == None:
                        correctA.deps = [nodeB]
                    else:
                        correctA.deps.append(nodeB)
            else:
                if correctB != None:
                    correctB.gov = nodeA
                    correctB.rel = edge['relation']
                    nodeA.deps = [correctB]
                else:
                    nodeB.gov = nodeA
                    nodeB.rel = edge['relation']
                    nodeA.deps = [nodeB]

    def add_node_pos(self, pos, index):
        ##Creates two nodes out of the edge
        text = ''
        try:
            text = pos['OriginalText']
        except Exception, e:
            text = pos['Text']
        nodeA = Node(text, index, pos['PartOfSpeech'], lemma = pos['Lemma'], 
                     start = pos['CharacterOffsetBegin'], end = pos['CharacterOffsetEnd'])

        curr = self.start
        
        if curr == None:
            ##If no nodes already in the ListTree, start at start
            self.start = nodeA
            self.end = nodeA
        else:
            ##Otherwise, go through each node starting at start and find the
            ##right place to insert the node
            prev = None 
            correctA = None
            while(curr != None and curr.index <= nodeA.index):
                if curr.index == nodeA.index:
                    curr.lemma = pos['Lemma']
                    break
                prev = curr
                curr = curr.nxt
            ##Insert the node
            if correctA == None:
                nodeA.nxt = curr
                nodeA.prev = prev
                if prev != None:
                    prev.nxt = nodeA
                if curr != None:
                    curr.prev = nodeA
                if self.start == nodeA.nxt:
                    self.start = nodeA
                if self.end == nodeA.prev:
                    self.end = nodeA

    def fixRoot(self):
        ##ListTree must already have a start or this won't work
        if self.start.index != 0:
            curr = self.start
            if self.start.gov == None:
                while curr.gov == None:
                    curr = curr.nxt
            prev = None
            if curr.top_ends():
                while curr != None:
                    prev = curr
                    curr = curr.gov
            else:
                found = []
                while curr != None:
                    if curr.gov != None:
                        if "VB" in curr.pos and "VB" not in curr.gov.pos:
                            break
                    if curr in found:
                        break
                    found.append(curr)
                    prev = curr
                    curr = curr.gov
            if curr == None:
                curr = prev
            if self.end.pos == '.':
                self.root = self.end
                self.end.deps = [curr]
                curr.gov = self.end
            else:
                temp = Node('SentEndDummy', 0, 'DMY', 'DMY')
                temp.deps = [curr]
                curr.gov = temp
                self.root = temp
        elif self.start.pos != '.':
            ##If the root/zero node isn't punctuation, remove it
            ##and replace it with a dummy node so traversal functions
            ##will be simpler
            temp = Node('SentEndDummy', 0, 'DMY', 'DMY')
            temp.deps = self.start.deps
            for dep in self.start.deps:
                dep.gov = temp
            self.start.deps = None
            self.start.gov = None
            self.start = self.start.nxt
            self.start.prev.prev = None
            self.start.prev.nxt = None
            self.start.prev = None
            self.root = temp
        else:
            ##If the root/zer0 node is punctuation, keep it, move it
            ##to the back of the sentence list and set it as the root
            if self.start.word == self.end.word:
                temp = self.start
                self.start = self.start.nxt
                self.start.prev = None
                self.end.prev.nxt = temp
                temp.prev = self.end.prev
                temp.nxt = None
                self.end = temp
                self.root = temp
                
            else:
                temp = self.start
                self.start = self.start.nxt
                self.start.prev = None
                self.end.nxt = temp
                temp.prev = self.end
                temp.nxt = None
                self.end = temp
                self.root = temp
            
    def search_and_descend(self, word):
        curr = self.start
        to_return = []
        while curr != None:
            if curr.word == word:
                deps = curr.get_descendents(curr.dist, False)
                if deps != None:
                    for dep in deps:
                        if dep not in to_return:
                            dep.commitment = True
                            to_return.append(dep)
            curr = curr.nxt
        return to_return
    
    def dists(self):
        self.root.build_dist(0)
        
    def get_quotes(self):
        to_return = []
        curr = self.start
        while ( curr != None):
            if curr.lemma == "``":
                found = []
                curr = curr.nxt
                while curr != None:
                    if curr.lemma == "''":
                        to_return.extend(found)
                        found = []
                        break
                    curr.commitment = True
                    found.append(curr)
                    if curr.nxt == None:
                        curr = curr.next_tree
                    else:
                        curr = curr.nxt
            elif curr.lemma == "`":
                found = []
                curr = curr.nxt
                while curr != None:
                    if curr.lemma == "'":
                        to_return.extend(found)
                        found = []
                        break
                    curr.commitment = True
                    found.append(curr)
                    if curr.nxt == None:
                        curr = curr.next_tree
                    else:
                        curr = curr.nxt


            if curr != None:
                if curr.nxt == None:
                    curr = curr.next_tree
                else:
                    curr = curr.nxt
        return to_return
    
    def get_question(self):
        to_return = None
        if self.root != None:
            if self.root.word == "?":
                to_return = self.root.get_descendents(self.root.dist, False)
                to_return.append(self.root)
        if to_return != None:
            for node in to_return:
                node.commitment = True
        return to_return
    
    def get_nodes(self, word, strip=False):
        ##get a list of nodes governed by word
        nodes = self.search_and_descend(word)
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
    
    def get_adv(self, adv):
        ##takes in an adverb, finds it in the dependency, pulls out everything
        ##the verb governing it governs
        verb = None
        curr = self.start
        to_return = []
        while (curr != None):
            if curr.word.lower() == adv:
                nodes = curr.gov.get_descendents(curr.gov.dist, False)
                verb = curr.gov
                curr.commitment = True
                to_return.append((verb, nodes))
            curr = curr.nxt
        return to_return

    def get_cond(self):
        antecedent = None
        resultant = None
        
        if self.start != None:
            curr = self.start
            while curr != None:
                if curr.word.lower() == 'if':
                    '''
                    print self
                    print curr
                    print "\n\n"
                    now = self.start
                    while now != None:
                        print now
                        now = now.nxt
                    '''
                    if curr.rel != "dep":
                        if curr.gov != None and curr.gov.gov != None:
                            if not (curr.gov.pos == "." or curr.gov.gov.pos == "." or curr.gov.rel == "parataxis" or curr.gov.gov.rel == "parataxis" or curr.gov.gov.pos == "DMY"):
                                if not (len(curr.gov.deps) <= 1):
                                    antecedent = curr.gov.get_descendents(curr.gov.dist, False)
                                    antecedent.append(curr.gov)
                                    resultant = [node for node in curr.gov.gov.get_descendents(curr.gov.gov.dist, False) if node not in antecedent]
                                    resultant.append(curr.gov.gov)
                                    for node in resultant:
                                        node.commitment = True
                                    for node in antecedent:
                                        node.commitment = True
                                    break
                curr = curr.nxt
        
        if antecedent != None:
            for node in antecedent:
                if node.nxt != None:
                    if node.nxt.pos == '.':
                        antecedent.append(node.nxt)
                    
        if resultant != None:            
            for node in resultant:
                if node.nxt != None:
                    if node.nxt.pos == '.':
                        resultant.append(node.nxt)
                                        
        return (antecedent, resultant)
    
    def get_neg(self):
        verbs = []
        all_none = []
        curr = self.start
        while curr != None:
            if curr.rel == 'neg':
                if "VB" in curr.gov.pos:
                    verbs.append(curr.gov)
                    all_none.extend(curr.gov.get_descendents(curr.dist, notStart = False))
            curr = curr.nxt
        return (verbs, all_none)
        
def build_ListTrees(deps, poses):
    ##Build a list of ListTrees from a list of deps
    ##Each dependency graph becomes its own tree
    listTree_list = []
    for num in range(len(deps)):
        ##For each dep(and pos in the future), build a ListTree
        ##and append it to the list
        dep = deps[num]
        pos = poses[num]
        if len(dep) < 1:
            continue
        if len(pos) < 1:
            continue
        tree = ListTree()
        for curr in range(len(pos)):
            tree.add_node_pos(pos[curr], curr+1)
        for edge in dep:            
            tree.add_node(edge)
        tree.fixRoot()
        if tree.root != None:
            tree.dists()
        listTree_list.append(tree)
    num = 0
    while (num+1 < len(listTree_list)):
        listTree_list[num].end.next_tree = listTree_list[num+1].start
        num += 1
    return listTree_list


if __name__ == '__main__':
    import json
    
    curr_file = "/home/random/workspace/Persuasion/data/convinceme/output_by_thread/1736/21585.json"
    j = json.load(open(curr_file))
    pos = j[0]
    deps = j[2]
    
    trees = build_ListTrees(deps, pos)
    
    for tree in trees:
        print tree
        
    quotes = trees[0].get_quotes()
    print
    print
    print quotes
    print 
    print