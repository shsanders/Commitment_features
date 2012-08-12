'''
Created on Aug 8, 2012

@author: random
'''
import operator
import Queue

def _annotate(text, tuples):
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

def annotate(text, tuples):
    start = first = operator.itemgetter(0)
    end  = second = operator.itemgetter(1)
    tag = operator.itemgetter(2)
    ordered = []
    start_tuples = sorted(tuples, key=start)
    for _tuple in start_tuples:
        ordered.append( (start(_tuple), '[{}]'.format(tag(_tuple))) )
    end_tuples = sorted(tuples, key=end)
    for _tuple in end_tuples:
        ordered.append( (end(_tuple), '[/{}]'.format(tag(_tuple))) )
    ordered = sorted(ordered, key=start)
    text2 = ''
    ordered.reverse()
    _abc = 0
    last = 0
    while len(ordered) > 0:
        _pop = ordered.pop()
        if last != first(_pop):
            last = first(_pop)
            text2 += text[_abc:last]
            _abc = last
        text2 += second(_pop)
    return text2

if __name__ == '__main__':

    test = "This is a test"
    tuples = [(0, 4, "this"), (5, 7, "is"), (8, 14, "done") ]
    
    ann = annotate(test, tuples)
    print ann
