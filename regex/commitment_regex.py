
import re, sys
from os.path import basename
import json
from collections import defaultdict
import operator
import nltk.stem

try:
    from discussion import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion import Dataset, data_root_dir
from nlp.text_obj import TextObj
from nlp import post
from nlp.boundary import Boundaries
from grab_data.convinceme_extras import get_topic_side
from file_formatting import arff_writer
from nlp.extract_contexts import _featlists


RUN_FOURFORUMS = False
POSTS_KEY = 'POSTS'
class CommitmentCounter(object):
    
    
    def __init__(self, label='side'):
        self.label = label
        self.freq = defaultdict(int)
        self.by_topic = defaultdict(lambda: defaultdict(int))
        self.by_side = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.stemmer = nltk.stem.PorterStemmer()
        self.feature_vectors_by_topic = defaultdict(lambda: list())
    
    def start(self):
        dataset = Dataset('convinceme',annotation_list=['side', 'topic','dependencies','used_in_wassa2011'])#'topic','dependencies'])
        for discussion in dataset.get_discussions(annotation_label='topic'):
            topic = discussion.annotations['topic']
            for post in discussion.get_posts():
                post.discussion_id = discussion.id
                post.topic_side = get_topic_side(discussion, post.side)
                post.key = str((discussion.id,post.id))
                
                result = self.extract(post, topic) 
                if result:
                    self.feature_vectors_by_topic[topic].append(result)
        
        for topic in self.feature_vectors_by_topic.keys():
            print '{topic} has {length} elements.'.format(**{'topic': topic, 'length': len(self.feature_vectors_by_topic[topic])})
        
        for topic in ['evolution']:
            minimum_inst = max(2, int(0.01 * len(self.feature_vectors_by_topic[topic])))
            output_dir = 'arffs'
            arff_writer.write("{}/all.arff".format(output_dir), 
                              self.feature_vectors_by_topic[topic], 
                              classification_feature=self.label, 
                              write_many=False, 
                              minimum_instance_counts_for_features=minimum_inst)
    
    
    def extract(self, post, topic, features=[]):
        if len(features) == 0: features = _featlists.keys()
        else: features = filter(lambda x: x in _featlists, features)
        spans = [] # span := [ span-id, [ start, stop, { "category": (major, minor), "environment_indicators": [ (word, occurrence_id) ] } ] ]
        for featpair in features:
            (word_pairs, phrase_pairs) = _featlists[featpair]
            occ_i = 0
            for word, rx in word_pairs:
                position = 0
                for sentence in re.split(r'\.!?', post.text):
                    match = rx.match(post.text)
                    if match:
                        spans.append( [ "%s-%s" % (str(post.id), len(spans)+1),
                                       [ position + match.start(),
                                        position + match.end(),
                                        { "category": featpair,
                                        "environment_indicators":
                                        [ (word, str(occ_i)) ] } ] ] )
                        position += len(sentence)
                        occ_i += 1
            occ_i = 0
            for phrase, rx in phrase_pairs:
                for m in rx.finditer(post.text):
                    spans.append( [ "%s-%s" % (str(post.id), len(spans)+1),
                                   [ m.start(),
                                    m.end(),
                                    { "category": featpair,
                                    "environment_indicators":
                                    [ (m.group(0), -1) ] } ] ] )
                    occ_i += 1
        self.by_topic[topic][POSTS_KEY] += 1
        environments = set()
        for span in set([d[1][2]['category'] for d in spans]):
            self.freq[span] += 1
            self.by_topic[topic][span] += 1
            self.by_side[topic][post.topic_side][span] += 1
            environments.add(span[0]) #XXX TODO need to make sure that the environments we are checking for are in the top three as far as probabiltiy goes
        if len(environments) < 2:
            #print 'throwing post away. discussion: {discussion} id: {id}'.format(**{'discussion': topic, 'id': post.id})
            return
        tuples = []
        for span in spans:
            start, stop, name = span[1][0], span[1][1], '-'.join(span[1][2]['category'])
            tuples.append((start,stop,name))
        b = Boundaries()
        b.initializeFromTuples(tuples)
        if len(b.boundaries) == 0: return
        b.walk(1, max(tuples, key=operator.itemgetter(1)))
        #print 'boundaries:{boundary.boundaries}\nparititions:{boundary.partitions}'.format(boundary=b)
        feature_vector = defaultdict(int)
        tokens = 0
        for partition in b.partitions[:-1]:
            unigrams = map(lambda unigram: self.stemmer.stem(unigram.lower()), re.split(r'\W', post.text[partition[0]:partition[1]]))
            tokens += len(unigrams)
            for _label in set(partition[2].split()):
                for unigram in unigrams:
                    feature_vector['commitment_{}:{}'.format(_label, unigram)] += 1
                    if _label == 'none':
                        feature_vector['collapsed_commitment:{unigram}'.format(unigram=unigram)] += 1
                    else:
                        feature_vector['collapsed_non_commitment:{unigram}'.format(unigram=unigram)] += 1
            for unigram in unigrams:
                feature_vector['unigram_{unigram}'.format(unigram=unigram)] += 1
        for key in feature_vector.keys():
            feature_vector[key] /= float(tokens)
        #print environments 
        feature_vector[self.label] = post.topic_side
        return feature_vector
    
    def start_(self):
        dataset = Dataset('fourforums',annotation_list=['qr_dependencies', 'topic'])#'topic','dependencies'])
        for discussion in dataset.get_discussions(annotation_label='mechanical_turk'):
            if 'qr_meta' not in discussion.annotations['mechanical_turk']: continue
            for post in discussion.get_posts():
                topic = discussion.annotations['topic']
                result = self.extract_(post, topic) 
                if result:
                    self.feature_vectors.append(result)
    
    def extract_(self, post, topic, features=[]):
        if len(features) == 0: features = _featlists.keys()
        else: features = filter(lambda x: x in _featlists, features)
        spans = [] # span := [ span-id, [ start, stop, { "category": (major, minor), "environment_indicators": [ (word, occurrence_id) ] } ] ]
        for featpair in features:
            (word_pairs, phrase_pairs) = _featlists[featpair]
            occ_i = 0
            for word, rx in word_pairs:
                position = 0
                for sentence in re.split(r'\.!?', post.text):
                    match = rx.match(post.text)
                    if match:
                        spans.append( [ "%s-%s" % (str(post.id), len(spans)+1),
                                       [ position + match.start(),
                                        position + match.end(),
                                        { "category": featpair,
                                        "environment_indicators":
                                        [ (word, str(occ_i)) ] } ] ] )
                        position += len(sentence)
                        occ_i += 1
            occ_i = 0
            for phrase, rx in phrase_pairs:
                for m in rx.finditer(post.text):
                    spans.append( [ "%s-%s" % (str(post.id), len(spans)+1),
                                   [ m.start(),
                                    m.end(),
                                    { "category": featpair,
                                    "environment_indicators":
                                    [ (m.group(0), -1) ] } ] ] )
                    occ_i += 1
        self.by_topic[topic][POSTS_KEY] += 1
        for span in set([d[1][2]['category'] for d in spans]):
            self.freq[span] += 1
            self.by_topic[topic][span] += 1
        #self.by_side[topic][post.topic_side][span] += 1
        
        tuples = []
        for span in spans:
            start, stop, name = span[1][0], span[1][1], '-'.join(span[1][2]['category'])
            tuples.append((start,stop,name))
        b = Boundaries()
        b.initializeFromTuples(tuples)
        if len(b.boundaries) == 0: return
        b.walk(1, max(tuples, key=operator.itemgetter(1)))
        feature_vector = defaultdict(int)
        for partition in b.partitions[:-1]:
            unigrams = map(lambda unigram: self.stemmer.stem(unigram.lower()), re.split(r'\W', post.text[partition[0]:partition[1]]))
            for unigram in unigrams:
                feature_vector['{}:{}'.format(partition[2], unigram)] += 1
        return feature_vector


if __name__ == '__main__':
    
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    
    if RUN_FOURFORUMS:
        doc = SimpleDocTemplate("simple_table4.pdf", pagesize=letter)
        fourforums = CommitmentCounter()
        fourforums.start_()
        OUTPUT = 'output4.out'
        fd = open(OUTPUT, 'w')
        data = []
        
        for topic in fourforums.by_topic:
            items = list(fourforums.by_topic[topic].iteritems())
            total = fourforums.by_topic[topic][POSTS_KEY]
            if total == 0: continue
            fd.write('{} {}\n'.format(topic, total))
            header = [topic, total, '']
            data.append(header)
            for ((key), value) in sorted(items, key=operator.itemgetter(1), reverse=True):
                if key == POSTS_KEY: continue
                percent = 100 * value / float(total)
                fd.write('\t{}\t\t{}\t{}\n'.format(key, value, str(percent)[:4]))
                if percent > 1:
                    datum = ['', '.'.join(key)[:12], str(percent)[:4]]
                    data.append(datum)
            data.append(['', '', ''])
        table = Table(data)
        table.setStyle(TableStyle([
                                   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ]))
        doc.build([table])
        fd.close()
    
    ## CONVINCEME
    doc = SimpleDocTemplate("simple_table.pdf", pagesize=letter)
    
    cc = CommitmentCounter()
    cc.start()
    items = list(cc.freq.iteritems())
    for ((key), value) in sorted(items, key=operator.itemgetter(1), reverse=True):
        print key, value 
    OUTPUT = 'output.out'
    fd = open(OUTPUT, 'w')
    SIDE_OUTPUT = 'side_output.out'
    fd_side = open(SIDE_OUTPUT, 'w')
    data = []
    for topic in cc.by_topic:
        items = list(cc.by_topic[topic].iteritems())
        total = cc.by_topic[topic][POSTS_KEY]
        if total == 0: continue
        fd.write('{} {}\n'.format(topic, total))
        side_a, side_b = cc.by_side[topic].keys()
        fd_side.write('{}({}):\n\t\t{}:\t{}:\n'.format(topic, total, side_a, side_b))
        header = [topic, total, '', '']
        sides = ['', '', side_a, side_b]
        data.append(header)
        data.append(sides)
        for ((key), value) in sorted(items, key=operator.itemgetter(1), reverse=True):
            if key == POSTS_KEY: continue
            fd.write('\t{}\t\t{}\t{}\n'.format(key, value, str(100 * value / float(total))[:4]))
            side_a_score = 100 * cc.by_side[topic][side_a][key]/ float(total)
            side_b_score = 100 * cc.by_side[topic][side_b][key]/ float(total)
            difference = abs(side_a_score - side_b_score)
            fd_side.write('\t{}:\t{}\t{}\t(diff:{})\n'.format(key, str(side_a_score)[:4], str(side_b_score)[:4], str(difference)[:4]))
            if side_a_score > 1 and side_b_score > 1:
                datum = ['', '.'.join(key)[:12], str(side_a_score)[:4], str(side_b_score)[:4]]
                data.append(datum)
        data.append(['', '', '', ''])
    table = Table(data)
    table.setStyle(TableStyle([
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ]))
    doc.build([table])
    fd.close()
    fd_side.close()
