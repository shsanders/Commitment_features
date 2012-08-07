#!/usr/bin/env python

## example / intended use:
#
# from post import Post
# p = Post.from_json('foo.json')
# print p.tree.to_string()
# p.tree.to_graphviz('foo') # creates "foo.dot", "foo.png"

import re
import json

import sys
import pdb

sys.path.append("../../utilities_external")
sys.path.append("../utilities_external")

sys.path.append("../")



from nlp import feature_extractor
from nlp import word_category_counter
import mpqa.mpqa as mpqa

from collections import Counter

import pdb

def toDict(l):
	voc = set(l)
	inds = range(len(voc))
	outDict = dict(zip(voc, inds))
	return outDict

def toLists(l):
	voc = set(l)
	return [[x] for x in voc]

class Post:
    # it is easier to use Post.from_json to create a Post instance
    # buildfeats: [] for build zero features, None for build all features
    def __init__(self, occurrences, deps, tree, sentstarts, sentends, postid, buildfeats=[], occMapping={}):
        self.occurrences = occurrences
        self.postid = postid
        self.dependencies = deps
        self.tree = tree
        self.sentstarts = sentstarts
        self.sentends = sentends
        self.text = ''.join([ o.before + o.text for o in occurrences ])
        # note that default behavior of build_features is to build a bunch of features,
        # but here in the constructor of Post, it is called in such a way as to build NO features by default        self.build_features(buildfeats) 
        self.features = dict()
        self.occMapping = occMapping

    def __repr__(self):
		return self.text

    def sentencesDB(self, site):
		starts = self.sentstarts
		ends = self.sentends
		lims = zip(starts, ends)
		sents = []
		i = 0
		for bounds in lims:
			try:
				sent = (i, self.text[bounds[0]: bounds[1]], bounds[0], bounds[1], self.tree.to_string(self.tree.roots[i]), self.postid, site)
				i += 1
			except:
				pdb.set_trace()
			sents.append(sent)
		return (toDict(sents), ["id", "text", "start", "end", "constituencyParse", "containingPost", "site"])
	
    def vocabDB(self):
		vocab = toDict([(x.text) for x in self.occurrences])
		return (vocab, ["word"])

    def posDB(self):
		POSvocab = toDict([(x.pos) for x in self.occurrences])
		return (POSvocab, ["pos"])
			
    def posWordsDB(self, vocabMap, POSMap):
    	try:
			POSWords = toDict([(x.text, x.pos) for x in self.occurrences])
    	except:
			pdb.set_trace()
    	return (POSWords, ["word", "pos"])
		
    def occurrencesDB(self, POSWordMap, vocabMap, POSMap, site):
		occs = []
		for i in range(len(self.occurrences)):
			try:
				occ = self.occurrences[i]
				sent=occ.getSent(self.sentstarts)
				o = (i, POSWordMap[(occ.text, occ.pos)], occ.text, occ.pos, occ.start, occ.end, self.postid, sent, site)
			except:
				pdb.set_trace()
			occs.append(o)
		return (toDict(occs), ["id", "POSword", "word", "pos", "start", "end", "containingPost", "sentence", "site"])
	
    def depRelsDB(self):
		depRels = toDict([(x.relation) for x in self.dependencies])
		return (depRels, ["relation"])

    def depsDB(self, POSWordMap, vocabMap, POSMap, occMap, depRelMap, site):
		deps = []
		for i in  range(len(self.dependencies)):
			dep = self.dependencies[i]
			relation = dep.relation
			gov_occ = self.occurrences[dep.gov_index]
			gov_v = vocabMap[gov_occ.text]
			gov_pos = POSMap[gov_occ.pos]
			gov_item = POSWordMap[(gov_occ.text, gov_occ.pos)]
			gov_ind = dep.gov_index
			
			dep_occ = self.occurrences[dep.dep_index]
			dep_v = vocabMap[dep_occ.text]
			dep_pos = POSMap[dep_occ.pos]
			dep_item = POSWordMap[(dep_occ.text, dep_occ.pos)]
			dep_ind = dep.dep_index			
			deps.append((i, relation, gov_ind, gov_occ.text, dep_ind, dep_occ.text, self.postid, site))		
		return (toDict(deps), ["id", "relation", "head", "headword", "tail", "tailword", "post", "site"])


    @staticmethod
    def from_stanford_nlp(pos_dicts=None, garbage=None, deps_dicts=None, post_id=0, buildfeats=False):

        #if postId != None:
        #    post_id = postId
        # ultimate goal: create a Post object
        # we can generate 3 of 5 parameters from the start
        try:
            occurrences = map(Occurrence, reduce(lambda x,y: x+y, pos_dicts))
        except TypeError, e:        # Something with one of the posts (empty post?) is causing this to fail reduce and it's ruining my life.
            return None
        occurrenceStarts = [o.start for o in occurrences]
        sent_starts = [ p[ 0][u'CharacterOffsetBegin'] for p in pos_dicts ]
        sent_ends   = [ p[-1][u'CharacterOffsetEnd']   for p in pos_dicts ]

        # walk through trees, re-indexing to make indices continue over sentence boundaries
        last_index = 0
        # params to create Tree
        roots = []
        parent = {}
        children = {}
        descendants = {}
        label = {}
        dependencies = []
        terminal = {}
        text = {}
        occMapping = {}
        for postnum in range(len(garbage)):
            tree = garbage[postnum]
            # parameters to Tree's constructor
            root_index = tree[u'index'] + last_index
            roots.append(root_index)

            # recursive walk, accumulating indices
            def walk(node, max_index):
                index = node[u'index'] + last_index
                if node[u'index'] > max_index: max_index = node[u'index']
                if node[u'parent'] is not None:
                    parent[index] = node[u'parent'] + last_index
                children[index] = map(lambda c: c[u'index'] + last_index, node[u'children'])
                descendants[index] = map(lambda d: d + last_index, node[u'dominates'])
                if node[u'token'] is None:  # if non-terminal
                    label[index] = node[u'label']
                    text[index] = None
                    terminal[index] = False
                else:
                    label[index] = node[u'token'][u'PartOfSpeech']
                    try:
                        text[index] = node[u'token'][u'OriginalText']
                    except KeyError:
                        text[index] = node[u'token'][u'Current']
                    terminal[index] = True
                    #                    pdb.set_trace()
                    occMapping[index] = occurrenceStarts.index(node[u'token'][u'CharacterOffsetBegin'])
                for child in node[u'children']:
                    max_index = walk(child, max_index)
                return max_index
            max_index = walk(tree, 0)

            # bump up dependancy dict indices, too
            for i in range(len(deps_dicts[postnum])):
                dependencies.append(
                    Dependency(
                        deps_dicts[postnum][i][u'relation'],
                        occMapping[deps_dicts[postnum][i][u'governor_index'] + last_index],
                        occMapping[deps_dicts[postnum][i][u'dependent_index'] + last_index]
                    )   )

            last_index += max_index

        tree = Tree(roots, parent, children, descendants, label, terminal, text, occMapping)
        return Post(occurrences, dependencies, tree, sent_starts, sent_ends, post_id, buildfeats, occMapping)



    @staticmethod
    def from_json(json_name, buildfeats=False, postId=0):
        #pos_dicts was previously called occdicts
        [pos_dicts, garbage, deps_dicts, post_id] = json.load(open(json_name))
        #if postId != None:
        #    post_id = postId
        # ultimate goal: create a Post object
        # we can generate 3 of 5 parameters from the start
        try:
            occurrences = map(Occurrence, reduce(lambda x,y: x+y, pos_dicts))
        except TypeError, e:        # Something with one of the posts (empty post?) is causing this to fail reduce and it's ruining my life.
            return None
        occurrenceStarts = [o.start for o in occurrences]
        sent_starts = [ p[ 0][u'CharacterOffsetBegin'] for p in pos_dicts ]
        sent_ends   = [ p[-1][u'CharacterOffsetEnd']   for p in pos_dicts ]

        # walk through trees, re-indexing to make indices continue over sentence boundaries
        last_index = 0
        # params to create Tree
        roots = []
        parent = {}
        children = {}
        descendants = {}
        label = {}
        dependencies = []
        terminal = {}
        text = {}
        occMapping = {}
        for postnum in range(len(garbage)):
            tree = garbage[postnum]
            # parameters to Tree's constructor
            root_index = tree[u'index'] + last_index
            roots.append(root_index)

            # recursive walk, accumulating indices
            def walk(node, max_index):
                index = node[u'index'] + last_index
                if node[u'index'] > max_index: max_index = node[u'index']
                if node[u'parent'] is not None:
                    parent[index] = node[u'parent'] + last_index
                children[index] = map(lambda c: c[u'index'] + last_index, node[u'children'])
                descendants[index] = map(lambda d: d + last_index, node[u'dominates'])
                if node[u'token'] is None:  # if non-terminal
                    label[index] = node[u'label']
                    text[index] = None
                    terminal[index] = False
                else:
                    label[index] = node[u'token'][u'PartOfSpeech']
                    try:
                        text[index] = node[u'token'][u'OriginalText']
                    except KeyError:
                        text[index] = node[u'token'][u'Current']
                    terminal[index] = True
                    #                    pdb.set_trace()
                    occMapping[index] = occurrenceStarts.index(node[u'token'][u'CharacterOffsetBegin'])
                for child in node[u'children']:
                    max_index = walk(child, max_index)
                return max_index
            max_index = walk(tree, 0)

            # bump up dependancy dict indices, too
            for i in range(len(deps_dicts[postnum])):
                dependencies.append(
                    Dependency(
                        deps_dicts[postnum][i][u'relation'],
                        occMapping[deps_dicts[postnum][i][u'governor_index'] + last_index],
                        occMapping[deps_dicts[postnum][i][u'dependent_index'] + last_index]
                    )   )

            last_index += max_index

        tree = Tree(roots, parent, children, descendants, label, terminal, text, occMapping)
        return Post(occurrences, dependencies, tree, sent_starts, sent_ends, post_id, buildfeats, occMapping)

    def to_string(self, *args):
        return self.tree.to_string(*args)

    def to_graphviz(self, *args):
        return self.tree.to_graphviz(*args)

    def to_json(self, json_name):
        f_json = open(json_name, 'w')
        json_top = []
        json_top.append(map(lambda o: o.to_json(), self.occurrences))
        json_top.append(map(lambda d: d.to_json(), self.dependencies))
        json_top.append(self.tree.to_json())
        json_top.append((self.sentstarts, self.sentends))
        json_top.append(self.features)
        json.dump(json_top, f_json)
        f_json.close()

    def to_feat_json(self, boundary=None):
        minIndex = self.occurrences[0].start
        maxIndex = self.occurrences[-1].end

        json_top = {}
        if boundary == None:
        	boundary = (minIndex, maxIndex, "none")
        json_top["bounds"] = boundary
        try:
        	json_top["text"] = self.text[boundary[0]:boundary[1]]
        except:
        	pdb.set_trace()
        json_top["features"] = self.features
        return json_top


    @staticmethod
    def from_own_json(json_name):
        f_json = open(json_name)
        [occ, deps, tree, (sstart, send), features] = json.load(f_json)
        f_json.close()
        occ = map(Occurrence.from_own_json, occ)
        deps = map(Dependency.from_own_json, deps)
        tree = Tree.from_own_json(tree)
        post = Post(occ, deps, tree, sstart, send)
        post.features = features
        return post

    def getIndex(self, lst, func, vals=None): #gets the first index that meets a certain criterion; used to bound occurrences and sentences
       for i,v in enumerate(lst):
           if func(v, vals):
              return i
       return None

    def build_features(self, feats=None, start=None, end=None): # default: None -> use default features
        minIndex = self.occurrences[0].start
        maxIndex = self.occurrences[-1].end

        if start is None:
           start = minIndex
        if end is None:
           end = maxIndex

        assert minIndex <= start <= maxIndex, "Start index is beyond bounds." 
        assert minIndex <= end <= maxIndex, "End index is beyond bounds." 
        assert start <= end, "Start index is greater than end index."

        startInd = self.getIndex(self.occurrences, lambda x,y: x.start>=y, start)
        endInd = self.getIndex(self.occurrences, lambda x,y: x.end>y, end)
        if endInd is None:
           endInd = len(self.occurrences)-1

        occurrences = self.occurrences[startInd:endInd]
        text = self.text[start:end]
        tokens = [o.text for o in occurrences]

        feature_dependencies_in = [d for d in self.dependencies if startInd <= d.gov_index < endInd  and startInd <= d.dep_index < endInd]

        feature_dependencies_boundary = [d for d in self.dependencies if startInd <= d.gov_index < endInd != startInd <= d.dep_index < endInd]

        # MPQA &c
        if feats is None:
            self.features = dict() # start fresh
            # default features
            feats = ['unigram', 'initialism', 'lengths', 'punctuation', 'quotes', 'liwc', 'dep']
        for feat in feats:
            if feat.endswith('gram'):
                n = measure_to_int(feat)
                feature_extractor.get_ngrams(self.features, tokens, n=n)
            elif feat.endswith('alism'):
                feature_extractor.get_initialisms(self.features, tokens, use_lowercase=True, finalism=(feat == 'finalism'))
            elif feat.startswith('lengths'):
                sentences = []
                numSents = len(self.sentstarts)
                for i in range(numSents):
                    if self.sentstarts[i] > end:
                       break
                    sStart = self.sentstarts[i]
                    sEnd = self.sentends[i]
                    if self.sentends[i] > start and self.sentstarts[i] < start:
                       sStart = start
                    elif self.sentends[i] > end and self.sentstarts[i] < end:
                       sEnd = end
                    sentences.append(self.text[sStart:sEnd])

                words = tokens
                feature_extractor.get_basic_lengths(self.features, text, sentences, words)
            elif feat.startswith('punct'):
                feature_extractor.get_repeated_punct(self.features, text)
            elif feat.startswith('quot'):
                feature_extractor.get_quoted_terms(self.features, text)
            elif feat.lower() == 'liwc':
                text_scores = Counter()
                text_scores['Word Count'] = len(occurrences)
                for o in occurrences:
                    text_scores.update(o.liwc)
                text_scores = word_category_counter.normalize(text_scores)
                for category, score in text_scores.items():
                    self.features['LIWC:'+category] = score
            elif feat.lower() == 'dep':
                dep_scores = Counter()
                #pdb.set_trace()
                for d in feature_dependencies_in:
                    dep_string = "%s(%s,%s)" % (d.relation, self.occurrences[d.gov_index].lemma, self.occurrences[d.dep_index].lemma)
                    dep_scores[dep_string] += 1
                for dep, score in dep_scores.items():
                    self.features['dep:'+ dep] = score


# feature vector building stuff
_measuredict = {'uni': 1, 'bi': 2, 'tri': 3}
rx_measure = re.compile(r'(\w+)gram')
def measure_to_int(s):
    m = rx_measure.match(s)
    if m is not None:
        m = m.group(1)
        if m in _measuredict: return _measuredict[m]
        return int(m)

class Occurrence:
    def __init__(self, postdict):
        self.text   = postdict.get(u'OriginalText',postdict.get(u'Current', ''))
        self.lemma  = postdict.get(u'Lemma')
        self.pos    = postdict.get(u'PartOfSpeech',None)
        self.start  = postdict.get(u'CharacterOffsetBegin',None)
        self.end    = postdict.get(u'CharacterOffsetEnd',None)
        self.before = postdict.get(u'Before', u'')
        self.after  = postdict.get(u'After', u'')
        self._liwc  = None # lazy evaluation via @property
        self.mpqa   = mpqa.lookup(self.text, self.pos)

    def __repr__(self):
		return ' '.join([str(x) for x in [self.text, self.pos, self.start, self.end]])

    @property
    def liwc(self):
        if self._liwc is None:
            self._liwc = dict(word_category_counter.score_word(self.text))
        return self._liwc

    def getSent(self,sentStarts):
		s = 0
		try:
			while self.start >= sentStarts[s]:
				s += 1
			return s-1
		except IndexError:
			return len(sentStarts)-1

    def to_json(self):
        return {
            u'text':   self.text,
            u'pos':    self.pos,
            u'start':  self.start,
            u'end':    self.end,
            u'before': self.before,
            u'after':  self.after,
            u'liwc':   self._liwc,
            u'mpqa':   self.mpqa,
        }

    @staticmethod
    def from_own_json(occmap, truncate=None):
        o = Occurrence({})
        o.text   = occmap[u'text']
        o.pos    = occmap[u'pos']
        o.start  = occmap[u'start']
        o.end    = occmap[u'end']
        o.before = occmap[u'before']
        o.after  = occmap[u'after']
        o._liwc   = occmap[u'liwc']
        o.mpqa   = occmap[u'mpqa']
        if truncate != None:
        	if len(o.text) > truncate:
        		o.text = o.text[:truncate]
        return o

class Dependency:
    def __init__(self, relation, gov_index, dep_index):
        self.relation = relation
        self.gov_index = gov_index
        self.dep_index = dep_index

    def __repr__(self):
		return ' '.join([str(x) for x in [self.gov_index, self.relation, self.dep_index]])

    def to_json(self):
        return {
            u'relation': self.relation,
            u'gov_index': self.gov_index,
            u'dep_index': self.dep_index,
        }

    @staticmethod
    def from_own_json(depmap):
        return Dependency(depmap[u'relation'],
                          depmap[u'gov_index'],
                          depmap[u'dep_index'])

class Tree:
    def __init__(self, roots, parent, children, descendants, label, terminal, text, occMapping):
        self.roots = roots
        self.parent = parent
        self.children = children
        self.descendants = descendants
        self.label = label
        self.terminal = terminal
        self.text = text
        self.occMapping = occMapping

    def to_graphviz(self, outname, root=None):
        def nodename(node):
            s = self.label[node]
            if self.terminal[node]:
                s += r' \"%s\"' % self.text[node].replace('"', r'\"')
            s += ' (%d)' % node
            return s

        if root is None: nodes = self.roots[:]
        elif hasattr(root, '__iter__'): nodes = root
        else: nodes = [root]

        outname = str(outname)
        f_out = open(outname+'.dot', 'w')
        print >>f_out, 'digraph G {'
        while len(nodes) > 0:
            parent = nodes.pop()
            children = self.children[parent]
            pname = nodename(parent)
            if len(children) == 0:
                print >>f_out, '    "%s";' % pname
            else:
                for child in children:
                    cname = nodename(child)
                    print >>f_out, '    "%s" -> "%s";' % (pname, cname)
                nodes.extend(children)
        print >>f_out, '}'
        f_out.close()
        from os import system
        return system('dot -T png -o %s.png %s.dot' % (outname, outname))

    def sentenceTrees(self):
		trees = []
		for root in self.roots:
			trees.append(self.to_string(root))
		return trees

    def sentenceTree(self, sentInd):
		if sentInd >= len(self.roots):
			return None
		else:
			return self.to_string(self.roots[sentInd])
		
    def to_string(self, root=None):
        # possible to make tail-recursive? danger of stack overflow... :[
        def to_string_aux(node):
            if self.terminal[node]:
            	if self.label[node] in ['-LRB-', '-RRB-']:
            		txt = "'%s'" % self.text[node]
            	else:
            		txt = "%s" % self.text[node]            	
                return r'( %s_%d %s )' % (self.label[node], node, txt)
            else:
                s = '( %s_%d' % (self.label[node], node)
                for child in self.children[node]:
                    s += ' %s' % (to_string_aux(child))
                s += ' )'
                return s

        if root is None: nodes = self.roots
        elif hasattr(root, '__iter__'): nodes = root
        else: nodes = [root]
        return ' '.join(map(to_string_aux, nodes))

    def __repr__(self):
		return self.to_string()
		
    def to_json(self):
        return {
            u'roots': self.roots,
            u'parent': self.parent,
            u'children': self.children,
            u'descendants': self.descendants,
            u'label': self.label,
            u'terminal': self.terminal,
            u'text': self.text,
            u'occMapping': self.occMapping
        }

    @staticmethod
    def from_own_json(treemap):
        for ugh in [u'parent', u'children', u'descendants', u'label', u'terminal', u'text', u'occMapping']:
            tmpdict = {}
            for k,v in treemap[ugh].iteritems():
                tmpdict[int(k)] = v
            treemap[ugh] = tmpdict
        return Tree(treemap[u'roots'],
                    treemap[u'parent'],
                    treemap[u'children'],
                    treemap[u'descendants'],
                    treemap[u'label'],
                    treemap[u'terminal'],
                    treemap[u'text'],
                    treemap[u'occMapping'])

#def same(first, second):
#    if type(first) != type(second):
#        print "type(first) != type(second); %s != %s" % (str(type(first)), str(type(second)))
#        return False
#    if isinstance(first, dict):
#        for k,v in first.iteritems():
#            if not second.has_key(k):
#                print "key %s in first, but not in second" % repr(k)
#                return False
#            if not same(v, second[k]):
#                print "first[k] != second[k]; first[%s] != second[%s]; %s != %s" % (repr(k), repr(k), repr(v), repr(second[k]))
#                return False
#    elif hasattr(first, '__iter__'):
#        if len(first) != len(second):
#            print "iterables of different lengths (%d and %d)" % (len(first), len(second))
#            return False
#        for i in range(len(first)):
#            if not same(first[i], second[i]):
#                print "first[i] != second[i]; first[%d] != second[%i]; %s != %s" % (i, i, repr(first[i]), repr(second[i]))
#                return False
#    elif isinstance(first, Occurrence) or isinstance(first, Dependency) or isinstance(first, Tree) or isinstance(first, Post):
#        for field in first.__dict__.keys():
#            if not same(first.__dict__[field], second.__dict__[field]):
#                print "field %s is not the same" % field
#                return False
#    else:
#        if first != second:
#            print "first != second; %s != %s" % (repr(first), repr(second))
#            return False
#    return True
#
#if __name__ == '__main__':
#    import sys
#    if len(sys.argv) < 2: name = "jsons/10004.json"
#    else: name = sys.argv[1]
#    post1 = Post.from_json(name)
#    post1.to_json('post1.json')
#    post2 = Post.from_own_json('post1.json')
#    print name, same(post1, post2)

# vim:set textwidth=0:
