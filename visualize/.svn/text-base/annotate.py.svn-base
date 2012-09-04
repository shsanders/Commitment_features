import operator
import re
import pdb

test = """Yes I have seen a dog cover it's own $hit before. You know that thing they do when they tear up the ground with their hind legs after they relieve themselves...that's covering it up.

As for the general topic at hand, dogs are better than cats becuase they actually care about their pack, which includes their owners. Cat's will love whomever feeds them/plays with them/picks up after them. Dogs have an attachment greater than their present dillema.

What cat has ever fought for something other than itself or its young? Lions and Siberian Tigers included. Dogs do it all the time out of loyalty to the pack."""

def annotate(text, tuples):
    start = first = operator.itemgetter(0)
    end  = second = operator.itemgetter(1)
    tag = operator.itemgetter(2)

    tuples.sort(key=start)
    tuples.reverse()
    for t in tuples:
        tagStr = tag(t).replace(' ', '_')
        s = '<span class="%s" title="%s">' % (tagStr, tagStr)
        e = '</span>'
        text = text[:start(t)] + s + text[start(t):end(t)] + e+ text[end(t):]
    return text

if __name__ == '__main__':

    tuples = [[452, 476, u'question'], [476, 491, u'none'], [491, 496, u'question'], [496, 512, u'none'], [512, 521, u'question']]    
    ann = annotate(test, tuples)
    print ann
