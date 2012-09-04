#!/usr/bin/python

import json
import os
import operator
import sys
import pdb
import cgi
#pdb.set_trace()
import svnUpdate

from collections import Counter

sys.path.append('..')
sys.path.append('/var/projects/persuasion/code')
sys.path.append('/var/projects/utilities/nlp')
from collections import defaultdict
try:
    from discussion import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion import Dataset, data_root_dir

import annotate

boundsFile = "bounds_dump"
DELETE_QUOTE = False

def generate_posts():
    dataset = Dataset('convinceme',annotation_list=['topic'])
    directory = "{}/convinceme/output_by_thread".format(data_root_dir)
    vals = []
   
    for thread in tuples.keys():
        for post in tuples[thread].keys():
            ed = Counter([x[-1] for x in tuples[thread][post] if x[-1] != "none"])
            vals.append((thread, post, ed))
    return write(vals)

def write(vals):
    vOut = ""
    for v in vals:
        vOut += """
    <div class="post"><a href="getSpans.py?thread=%s&post=%s" target="_BLANK">%s %s %s</a></div>""" % (v[0], v[1], v[0], v[1], ' | '.join(sorted(v[2].keys())))

    r = """Content-Type: text/html; charset=utf-8


<html>
<head>
	<style type="text/css">
#author {color: red;}
#side {color: green;}
#text {margin: 5px; border: 1px dotted red;}
#post {width: 400px;}
span  {border: 1px dotted black;}
.none {background-color: gray}
	</style>
</head>
<body>
%s
</body>
</html>""" % (vOut)
    return r

def loadTuples():
    global tuples
    svnUpdate.update()
    fin = open(boundsFile, "r")
    tuples = json.load(fin)

if  __name__ == '__main__':
    loadTuples()
    print generate_posts()
