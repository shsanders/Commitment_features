#!/usr/bin/env python

import json
import os
import operator
import sys
import re
import random

from collections import defaultdict, Counter

try:
    from discussion import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion import Dataset, data_root_dir
    
from file_formatting import arff_writer
from nlp.text_obj import TextObj
from nlp.feature_extractor import get_features_by_type, get_dependency_features
from nlp.boundary import Boundaries
from grab_data.convinceme_extras import get_topic_side

sys.path.append('..')
from get_features import feat_vect
from annotate import annotate

from utils import ngrams_from_text

DELETE_QUOTE = False

rand = []

def merrrr(text, boundaries):
        return ["{}:{}".format(bound[2].upper(), re.sub(r'\r', '', text)[bound[0]:bound[1]]) for bound in boundaries]

def uni_from_boundaries(text, boundaries, features):
    bounds = [(bound[2].upper(), re.sub(r'\r', '', text)[bound[0]:bound[1]]) for bound in boundaries]
    for bound in bounds:
        ngrams_from_text(bound[1], features, prefix=bound[0]+"_uni_caps_", n=1, style='float')
        ngrams_from_text(bound[1].lower(), features, prefix=bound[0]+"_uni_lower_", n=1, style='float')

class Bounds(object):
    def __init__(self, output='bounds_dump'):
        self._dict = defaultdict(lambda: defaultdict(list))
        self._output = output
        
    def add(self, discussion_id, post_id, text, tuples):
        boundaries = Boundaries()
        boundaries.initializeFromTuples(tuples)
        try:
            boundaries.walk(0, max(tuples, key=operator.itemgetter(1)))
            self._dict[discussion_id][post_id] = boundaries.partitions
            rand.append([text, merrrr(text, tuples), tuples, discussion_id, post_id])
        except ValueError, e:
            pass

    def dump(self):
        print 'Dumping Boundaries to {}.'.format(self._output)
        json.dump(self._dict, open(self._output, 'wb'))

class Commitment(object):


    def __init__(self, topic, features=['unigram', 'LIWC', 'pos_dep']):
        self.topic = topic
        self.feature_vectors = []
        self.classification_feature = 'commitment'
        self.features = features
        self.bounds = Bounds()
        self.dir = re.sub(r'\s+', '_', topic)

    def generate_features(self):
        dataset = Dataset('convinceme',annotation_list=['topic','dependencies','used_in_wassa2011', 'side'])
        directory = "{}/convinceme/output_by_thread".format(data_root_dir)
        for discussion in dataset.get_discussions(annotation_label='topic'):
            if self.topic != discussion.annotations['topic']:
                continue
            for post in discussion.get_posts():

                feature_vector = defaultdict(int)
                post.discussion_id = discussion.id
                post.topic_side = get_topic_side(discussion, post.side)
                post.key = str((discussion.id,post.id))
                feature_vector[self.classification_feature] = post.topic_side
                try:

                    json_file = "{}/{}/{}.json".format(directory, discussion.id, post.id)
                    pos, parsetree, dep, ident = json.load(open(json_file, 'r'))
                    result = sorted(feat_vect(dep, pos, feature_vector), key=operator.itemgetter(0))
                    try:
                        text = TextObj(post.text.decode('utf-8', 'replace'))
                    except Exception, e:
                        continue

                    self.bounds.add(discussion_id=discussion.id, post_id=post.id, text=text.text, tuples=result)
                    
                    uni_from_boundaries(text.text, result, feature_vector)

                    dependency_list = None if 'dependencies' not in post.annotations else post.annotations['dependencies']
                    if 'unigram' in self.features:
                        ngrams_from_text(text.text.lower(), feature_vector, prefix="uni_lower_", n=1, style='float')
                        ngrams_from_text(text.text, feature_vector, prefix="uni_caps_", n=1, style='float')
                    feats = set(self.features).difference(set(['unigram']))
                    get_features_by_type(feature_vector=feature_vector, features=feats, text_obj=text, dependency_list=dependency_list)

                    
                    if None == dependency_list: continue
                    if 'dependencies' in self.features:
                        get_dependency_features(feature_vector, dependency_list, generalization='opinion')  

                    if DELETE_QUOTE:
                        unigrams = map(lambda x: x[8:], filter(lambda x: x.startswith('unigram:'), feature_vector.keys()))
                        for unigram in unigrams:
                            key = 'quote: {}'.format(unigram)
                            if key in feature_vector:
                                del feature_vector[key]

                    self.feature_vectors.append(feature_vector)

                except IOError, e:
                    # XXX TODO : we don't have all the parses saved apparently so this sometimes fails.
                    pass
        self.bounds.dump()

    def generate_arffs(self, output_dir='arffs_output'):
        if not self.feature_vectors:
            return
        types = set()
        output_dir = "{}/{}".format(output_dir, self.dir)
        minimum_inst = max(2, int(0.01 * len(self.feature_vectors)))
        
        arff_writer.write("{}/all.arff".format(output_dir), 
                        self.feature_vectors, 
                        classification_feature=self.classification_feature, 
                        write_many=False, 
                        minimum_instance_counts_for_features=minimum_inst)
        regex = re.compile(r'(.*)_uni_(.*)$')
        commitment = ['NONE', 'CONSEQUENT']
        non_commitment = ['ANTECEDENT', 'QUOTE', 'QUESTION']
        collapsed_dicts = []
        for vector in self.feature_vectors:
            _modified = dict()
            for key, value in vector.iteritems():
                result = regex.match(key)
                if result:
                    types.add(result.group(1))
                    if result.group(1) in commitment:
                        _modified['commitment: {}'.format(result.group(2))] = value
                    elif result.group(1) in non_commitment:
                        _modified['non_commitment: {}'.format(result.group(2))] = value
                _modified[key] = vector[key]
            collapsed_dicts.append(_modified)

        arff_writer.write("{}/all_collapsed.arff".format(output_dir),
                    collapsed_dicts, 
                    classification_feature=self.classification_feature, 
                    write_many=False, 
                    minimum_instance_counts_for_features=minimum_inst)


    def main(self):
        self.generate_features()
        self.generate_arffs()

if  __name__ == '__main__':
    for topic in ['death penalty', 'gay marriage', 'existence of god', 'evolution']:
        commitment = Commitment(topic=topic, features=['unigram'])
        commitment.main()
        fd = open('dump_random_'+re.sub(' ', '_', topic), 'wb')
        for line in random.sample(rand, 10):
            text, annots, raw, discussion, post = line
            fd.write("Discussion:{}, Post:{}\n".format(discussion, post))
            fd.write("TEXT:{}\n".format(text))
            for annotation in annots:
                fd.write("{}\n".format(annotation))
            fd.write("RAW:{}\n\n".format(raw))
            #fd.write("ANNOTS:{}\n\n".format(annots))
        fd.close()

