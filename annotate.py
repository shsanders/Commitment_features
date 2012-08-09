'''
Created on Aug 8, 2012

@author: random
'''

import Queue

def annotate(text, tuples):
    ends = []
    newText = "";
    curr = 0;
    for point in tuples:
        if len(ends) > 0:
            while (ends[0][0] <= point[0]):
                end = ends.pop(0)
                newText += text[curr:end[0]] + "[\\" + end[1] + "]"
                curr = end[0]
                if len(ends) < 1:
                    break
        newText += text[curr:point[0]] + "[" + point[2] + "]"
        curr = point[0]
        ends.append((point[1], point[2]))
    for end in ends:
        end = ends.pop(0)
        newText += text[curr:end[0]] + "[\\" + end[1] + "]"
        curr = end[0]
    newText += text[curr:]
    
    return newText

if __name__ == '__main__':

    test = "This is a test"
    tuples = [(0, 4, "this"), (5, 7, "is"), (8, 14, "done") ]
    
    ann = annotate(test, tuples)
    print ann
        
        