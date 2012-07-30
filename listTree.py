'''
Created on Jul 19, 2012

ListTree class fully functional (for the time being). Build a new list of 
ListTrees by calling the function build_ListTrees on a list of semantic
dependnecies. Each dependency graph will be turned into its own tree.
    
Two ways to parse it (I'm using LT to be a generic ListTree): 
starting at the front using LT.start or by starting
at the root by using LT.root. If you're trying to find a specific word, you
would probably want something like this:

curr = LT.start
while (curr != None):
    if curr.word == word:
        break
    curr = curr.nxt

curr will end up being the right node, or it will be None

The dependents of a node are node.deps, and they are a list. So, you would want
to create a function that takes in lists if you were trying to figure out what the
descendents of a node are. Something like

def find_descend(deps):
    descendents = deps
    for dep in deps:
        descendents.extend(find_descend(dep.deps))
    return descendents
    

@author: random
'''

class Node:
    '''
    Node class for ListTree
    Nodes are connected in governor-relation manner and in
    linear first-last sentence order
    each node contains info about that word
    nxt = next, prev = previous, gov = governor, deps = list of dependents
    everything else is information about the word
    '''

    def __init__(self, word, index, pos, rel):
        '''
        constructor
        '''
        self.gov = None
        self.deps = None
        self.prev = None
        self.nxt = None
        self.dist = None
        self.pos = pos
        self.word = word
        self.index = index
        self.rel = rel
        
    def __repr__(self):
        ##Prints in the format 
        ##index: word, pos, rel,
        ##gov:
        ##deps:
        ##prev:
        ##nxt:
        to_return = str(self.index) + ": " + self.word + ", " + self.pos + ", " + str(self.rel) + "\ngov: "
        if self.gov != None:
            to_return += self.gov.word
        to_return += "\ndeps: "
        if self.deps != None:
            for node in self.deps:
                to_return += node.word + " "
        to_return += "\n"
        to_return += "prev: "
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
                    deps.extend(des)
        return deps
    
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
        curr = self.start
        while (curr != None):
            to_return += "\n"
            to_return += str(curr)
            curr = curr.nxt
        return to_return
            

    def add_node(self, edge):
        ##Creates two nodes out of the edge
        nodeA = Node(edge['governor'], edge['governor_index'], edge['governor_pos'], None)
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

    def fixRoot(self):
        ##ListTree must already have a start or this won't work
        if self.start.index != 0:
            return
        if self.start.pos != '.':
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
                            to_return.append(dep)
            curr = curr.nxt
        return to_return
    
    def dists(self):
        self.root.build_dist(0)
        

def build_ListTrees(deps):
    ##Build a list of ListTrees from a list of deps
    ##Each dependency graph becomes its own tree
    listTree_list = []
    for num in range(len(deps)):
        ##For each dep(and pos in the future), build a ListTree
        ##and append it to the list
        dep = deps[num]
        if len(dep) < 1:
            continue
        tree = ListTree()
        for edge in dep:
            tree.add_node(edge)
        if tree.start == None:
            print "Shitty dep:"
            print dep
        tree.fixRoot()
        tree.dists()
        listTree_list.append(tree)
    return listTree_list

'''
from nlp.stanford_nlp import get_parses

sent = "I admit that I like cookies"

print sent

parse = get_parses(sent)

print parse[2]

trees = build_ListTrees(parse[2])

for tree in trees:
    print "Final tree: "
    print tree
    print "\n"
    
    deps = tree.search_and_descend("admit")
    for dep in deps:
        print dep
'''