'''
Created on Jul 19, 2012

ListTree currently functional. I don't have a way of picking the
root node for the tree version, but it seems solid besides that. No issues
with infinite loops at the moment, but that could change as the tree
functions are build and tinkered.

@author: random
'''

class Node:
    '''
    Node class for ListTree
    Nodes are connected in governor-relation manner and in
    linear first-last sentence order
    each node contains info about that word
    '''

    def __init__(self, word, index, pos):
        '''
        constructor
        '''
        self.gov = None
        self.deps = None
        self.prev = None
        self.nxt = None
        self.pos = pos
        self.word = word
        self.index = index
        
    def __repr__(self):
        ##Prints in the format 
        ##index: word: pos: 
        ##gov:
        ##deps:
        to_return = str(self.index) + ": " + self.word + ", " + self.pos + "\ngov: "
        if self.gov != None:
            to_return += self.gov.word
        to_return += "\ndeps: "
        if self.deps != None:
            for node in self.deps:
                to_return += node.word + " "
        to_return += "\n"
        return to_return
        
class ListTree:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
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
            to_return += str(curr)
            curr = curr.nxt
        return to_return
            

    def add_node(self, edge):
        ##Creates two nodes out of the edge
        nodeA = Node(edge['governor'], edge['governor_index'], edge['governor_pos'])
        nodeB = Node(edge['dependent'], edge['dependent_index'], edge['dependent_pos'])
        
        ##Fills the gov and deps fields as needed
        nodeA.deps = [nodeB]
        nodeB.gov = nodeA
        
        curr = self.start
        
        if curr == None:
            ##If no nodes already in the ListTree, start at start
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
                    correctB.gov = correctA
                    if correctA.deps == None:
                        correctA.deps = [correctB]
                    else:
                        correctA.deps.append(correctB)
                else:
                    if correctA.deps == None:
                        correctA.deps = [nodeB]
                    else:
                        correctA.deps.append(nodeB)
            else:
                if correctB != None:
                    correctB.gov = nodeA

    def fixRoot(self):
        ##ListTree must already have a start or this won't work
        if self.start.index != 0:
            return
        if self.start.pos != '.':
            ##If the root/zero node isn't punctuation, remove it
            ##and replace it with a dummy node so traversal functions
            ##will be simpler
            temp = Node('SentEndDummy', 0, "DMY")
            temp.deps = self.start.deps
            self.start = self.start.nxt
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
            

def build_ListTrees(deps):
    ##Build a list of ListTrees from a list of deps
    ##Each dependency graph becomes its own tree
    listTree_list = []
    for num in range(len(deps)):
        ##For each dep(and pos in the future), build a ListTree
        ##and append it to the list
        tree = ListTree()
        dep = deps[num]
        for edge in dep:
            tree.add_node(edge)
        listTree_list.append(tree)
    for listTree in listTree_list:
        listTree.fixRoot()
    return listTree_list


from nlp.stanford_nlp import get_parses

sent = "I admit that I like cookies"

print sent

parse = get_parses(sent)

print parse[2]

trees = build_ListTrees(parse[2])

for tree in trees:
    print tree
