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
from convinceme_extras import add_info_to_posts

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
        self.classification_feature = 'side'
        self.features = features
        self.bounds = Bounds()
        self.dir = re.sub(r'\s+', '_', topic)

    def generate_features(self):
        print 'Generating features for topic: {}'.format(self.topic)
        dataset = Dataset('convinceme',annotation_list=['side', 'topic','dependencies','used_in_wassa2011'])#'topic','dependencies'])
        directory = "{}/convinceme/output_by_thread".format(data_root_dir)
        discussions = list(dataset.get_discussions(annotation_label='topic'))
        add_info_to_posts(discussions)
        for discussion in discussions:
            if self.topic != discussion.annotations['topic']:
                continue
            for post in discussion.get_posts():

                feature_vector = defaultdict(int)
                
                try:

                    json_file = "{}/{}/{}.json".format(directory, discussion.id, post.id)
                    pos, parsetree, dep, id = json.load(open(json_file, 'r'))
                    result = sorted(feat_vect(dep, pos, feature_vector), key=operator.itemgetter(0))
                    try:
                        text = TextObj(post.text.decode('utf-8', 'replace'))
                    except Exception, e:
                        continue

                    self.bounds.add(discussion_id=discussion.id, post_id=post.id, text=text.text, tuples=result)

                    dependency_list = None if 'dependencies' not in post.annotations else post.annotations['dependencies']
                    get_features_by_type(feature_vector=feature_vector, features=self.features, text_obj=text, dependency_list=dependency_list)

                    if None == dependency_list: continue
                    if 'dependencies' in self.features:
                        get_dependency_features(feature_vector, dependency_list, generalization='opinion')  

                    if DELETE_QUOTE:
                        unigrams = map(lambda x: x[8:], filter(lambda x: x.startswith('unigram:'), feature_vector.keys()))
                        for unigram in unigrams:
                            key = 'quote: {}'.format(unigram)
                            if key in feature_vector:
                                if key in feature_vector: 
                                    del feature_vector[key]


                    feature_vector[self.classification_feature] = post.topic_side#self.get_label(discussion=discussion, post=post)
                    self.feature_vectors.append(feature_vector)

                except IOError, e:
                    # XXX TODO : we don't have all the parses saved apparently so this sometimes fails.
                    pass
            #OCCURS LESS THAN 10 TIMES
            """
            freq = defaultdict(int)
            for vector in self.feature_vectors:
                for key in vector.keys():
                    freq[key] += 1

            for vector in self.feature_vectors:
                for key, value in freq.iteritems():
                    if float(value / float(len(self.feature_vectors))) < 0.02:
                        if key in vector:
                            del vector[key]
            """     


        self.bounds.dump()

    def generate_arffs(self, output_dir='arffs_output'):
        if not self.feature_vectors:
            return
        types = set()
        output_dir = "{}/{}".format(output_dir, self.dir)
        minimum_inst = int(0.02 * len(self.feature_vectors)) #max(2, int(0.01 * len(self.feature_vectors)))
        arff_writer.write("{}/wassa.arff".format(output_dir), 
                        self.feature_vectors, 
                        classification_feature=self.classification_feature, 
                        write_many=False, 
                        minimum_instance_counts_for_features=minimum_inst)
        regex = re.compile(r'(.*): unigram: (.*)$')
        commitment = ['none', ]#'consequent']
        non_commitment = ['antecedent', 'quote', 'question', 'consequent']
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
                if not key[:4] in map(lambda x: x[:4], commitment + non_commitment):
                    _modified[key] = vector[key]
            collapsed_dicts.append(_modified)

        arff_writer.write("{}/wassa_collapsed.arff".format(output_dir),
                    collapsed_dicts, 
                    classification_feature=self.classification_feature, 
                    write_many=False, 
                    minimum_instance_counts_for_features=minimum_inst)
        print types


    def main(self):
        self.generate_features()
        self.generate_arffs()

    def get_label(self, discussion, post):
        #return post.side == max(discussion.annotations['side'], key=operator.itemgetter(1))[0]
        return 'for' if post.side == discussion.annotations['side'][0][0] else 'against'

if  __name__ == '__main__':
    for topic in ['evolution', 'existence of god', 'gay marriage']:
        commitment = Commitment(topic=topic, features=['pos_dep', 'liwc_dep', 'gen', 'unigrams', 'liwc', 'opin'])
        commitment.main()
        fd = open('dump_random', 'wb')
        for line in random.sample(rand, 10):
            text, annots, raw = line
            fd.write("TEXT:{}\n".format(text))
            for annotation in annots:
                fd.write("{}\n".format(annotation))
            fd.write("RAW:{}\n\n".format(raw))
            #fd.write("ANNOTS:{}\n\n".format(annots))
        fd.close()


