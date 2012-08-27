#!/usr/bin/env python

import json
import os
import operator
import sys
import re
import random

from collections import defaultdict
try:
    from discussion import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion import Dataset, data_root_dir

from file_formatting import arff_writer
from nlp.text_obj import TextObj
from nlp.feature_extractor import get_features_by_type, get_dependency_features
from nlp.boundary import Boundaries
from convinceme_extras import get_topic_side

sys.path.append('..')
from get_features import feat_vect
from annotate import annotate

DELETE_QUOTE = True

rand = []

def merrrr(text, boundaries):
        return ["{}:{}".format(bound[2].upper(), re.sub(r'\r', '', text)[bound[0]:bound[1]]) for bound in boundaries]

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
            #if len(boundaries.partitions) == 0: return
            #print annotate(text, boundaries.partitions[:-1])
            #rand.append([annotate(text, boundaries.partitions[:-1]), tuples, boundaries.partitions[:-1]])
            rand.append([text, merrrr(text, tuples), tuples])
        except ValueError, e:
            pass

    def dump(self):
        print 'Dumping Boundaries to {}.'.format(self._output)
        json.dump(self._dict, open(self._output, 'wb'))

class Commitment(object):


    def __init__(self, topic='death penalty', features=['unigram', 'LIWC', 'pos_dep']):
        self.topic = topic
        self.feature_vectors = []
        self.classification_feature = 'commitment'
        self.features = features
        self.bounds = Bounds()
        self.dir = re.sub(r'\s+', '_', topic)

    def generate_features(self, no_commit = False):
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
                    pos, parsetree, dep, id = json.load(open(json_file, 'r'))
                    result = sorted(feat_vect(dep, pos, feature_vector), key=operator.itemgetter(0))
                    try:
                        text = TextObj(post.text.decode('utf-8', 'replace'))
                    except Exception, e:
                        continue

                    self.bounds.add(discussion_id=discussion.id, post_id=post.id, text=text.text, tuples=result)

                    if not no_commit:
                        dependency_list = None if 'dependencies' not in post.annotations else post.annotations['dependencies']
                        sys.path.append('/Users/samwing/nldslab/old_persuasion/persuasion/old/code')
                        
                        if 'unigram' in self.features:
                            from old_features import get_ngrams
                            from utils import flatten
                            from parser import tokenize
                            sentences = tokenize(text.text.lower(), break_into_sentences=True)
                            words_flat = flatten(sentences)
                            get_ngrams(feature_vector=feature_vector, words=words_flat)
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
                    
                    else:
                        dependency_list = None if 'dependencies' not in post.annotations else post.annotations['dependencies']
                        get_features_by_type(feature_vector=feature_vector, text_obj=text, dependency_list=dependency_list)

                    self.feature_vectors.append(feature_vector)

                except IOError, e:
                    # XXX TODO : we don't have all the parses saved apparently so this sometimes fails.
                    pass
        self.bounds.dump()

    def generate_arffs(self, output_dir='arffs_output', no_commit = False):
        if not self.feature_vectors:
            return
        types = set()
        output_dir = "{}/{}".format(output_dir, self.dir)
        minimum_inst = max(2, int(0.01 * len(self.feature_vectors)))
        
        if not no_commit:
            arff_writer.write("{}/all.arff".format(output_dir), 
                            self.feature_vectors, 
                            classification_feature=self.classification_feature, 
                            write_many=False, 
                            minimum_instance_counts_for_features=minimum_inst)
            regex = re.compile(r'(.*): unigram: (.*)$')
            commitment = ['none', 'consequent']#'consequent']
            non_commitment = ['antecedent', 'quote', 'question']
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
            print types
            
        else:
            arff_writer.write("{}/baseline.arff".format(output_dir), 
                self.feature_vectors, 
                classification_feature=self.classification_feature, 
                write_many=False, 
                minimum_instance_counts_for_features=minimum_inst)


    def main(self, no_commit = False):
        self.generate_features(no_commit=no_commit)
        self.generate_arffs(no_commit=no_commit)

if  __name__ == '__main__':
    for topic in ['gay marriage']:
        commitment = Commitment(topic=topic, features=['unigram'])
        commitment.main()
        #commitment = Commitment(topic=topic, features=[])
        #commitment.main(no_commit = True)
        fd = open('dump_random', 'wb')
        for line in random.sample(rand, 10):
            text, annots, raw = line
            fd.write("TEXT:{}\n".format(text))
            for annotation in annots:
                fd.write("{}\n".format(annotation))
            fd.write("RAW:{}\n\n".format(raw))
            #fd.write("ANNOTS:{}\n\n".format(annots))
        fd.close()

