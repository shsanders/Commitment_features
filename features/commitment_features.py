#!/usr/bin/env python

import json
import os
import operator
import sys
try:
    from discussion import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion import Dataset, data_root_dir

from file_formatting import arff_writer
from nlp.text_obj import TextObj
from nlp.feature_extractor import get_features_by_type

sys.path.append('..')
from get_features import feat_vect

DELETE_QUOTE = True

class Commitment(object):


    def __init__(self, topic='death penalty', features=['unigram', 'LIWC', 'pos_dep']):
        self.topic = topic
        self.feature_vectors = []
        self.classification_feature = 'commitment'
        self.features = features

    def generate_features(self):
        dataset = Dataset('convinceme',annotation_list=['topic','dependencies'])
        directory = "{}/convinceme/output_by_thread".format(data_root_dir)
        for discussion in dataset.get_discussions(annotation_label='topic'):
            if self.topic != discussion.annotations['topic']:
                continue
            for post in discussion.get_posts():

                feature_vector = dict()
                
                try:

                    json_file = "{}/{}/{}.json".format(directory, discussion.id, post.id)
                    pos, parsetree, dep, id = json.load(open(json_file, 'r'))
                    result = sorted(feat_vect(dep, pos, feature_vector), key=operator.itemgetter(0))
                    print result
                    # [('Question', 0, 1), . .. ('Cond', 3, 4)]
                    try:
                        text = TextObj(post.text.decode('utf-8', 'replace'))
                    except Exception, e:
                        continue

                    dependency_list = None if 'dependencies' not in post.annotations else post.annotations['dependencies']
                    get_features_by_type(feature_vector=feature_vector, features=self.features, text_obj=text, dependency_list=dependency_list)

                    if DELETE_QUOTE:
                        unigrams = map(lambda x: x[8:], filter(lambda x: x.startswith('unigram:'), feature_vector.keys()))
                        for unigram in unigrams:
                            key = 'quote: {}'.format(unigram)
                            if key in feature_vector:
                                del feature_vector[key]

                    feature_vector[self.classification_feature] = self.get_label(discussion=discussion, post=post)
                    self.feature_vectors.append(feature_vector)

                except IOError, e:
                    # XXX TODO : we don't have all the parses saved apparently so this sometimes fails.
                    pass

    def generate_arffs(self, output_dir='arffs_output'):
        if not self.feature_vectors:
            return
        minimum_inst = max(2, int(0.01 * len(self.feature_vectors)))
        arff_writer.write("{}/all.arff".format(output_dir), 
                        self.feature_vectors, 
                        classification_feature=self.classification_feature, 
                        write_many=False, 
                        minimum_instance_counts_for_features=minimum_inst)

    def main(self):
        self.generate_features()
        self.generate_arffs()

    def get_label(self, discussion, post):
        #return post.side == max(discussion.annotations['side'], key=operator.itemgetter(1))[0]
        return post.side == discussion.annotations['side'][0][0]

if  __name__ == '__main__':
    commitment = Commitment()
    commitment.main()
