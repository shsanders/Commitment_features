'''
Created on Jul 19, 2012

@author: random
'''

class Node:
    '''
    Node class for ListTree
    Nodes are connected in governor-relation manner and in
    linear first-last sentence order
    each node contains info about that word
    '''

    def _init_(self, gov=None, deps=None, prev=None, nxt=None, word, index):
        '''
        constructor
        '''
        self.gov = gov
        self.deps = deps
        self.prev = prev
        self.nxt = nxt
        self.word = word
        self.index = index

class ListTree:
    '''
    classdocs
    '''

    def __init__(self, start=None, root=None):
        '''
        Constructor
        '''
        self.start = start
        self.root = root
                
    def add_nodes(self, edge, pos):
        indA = edge['governor_index']
        indB = edge['dependent_indx']
        
        curr = self.start       
        prev = None 
        correct = None
        while(curr != None and curr.index < indA):
            if curr.index == indA:
                correct = curr
                break
            prev = curr
            curr = curr.nxt
            
        if correct != None:
            
            
        curr = self.start
        prev = None
        while(curr != None and curr.index < indA):
            prev = curr
            curr = curr.nxt
            
    

    def build_ListTree(self, deps, pos):
        for num in range(len(deps)):
            dep = deps[num]
            