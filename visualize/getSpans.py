#!/usr/bin/python

import json
import os
import operator
import sys
import pdb
import cgi
#pdb.set_trace()
import svnUpdate


sys.path.append('..')
sys.path.append('/var/projects/persuasion/code')
sys.path.append('/var/projects/utilities/nlp')
from collections import defaultdict
try:
    from discussion_with_posts import Dataset, data_root_dir
except Exception, e:
    from grab_data.discussion_with_posts import Dataset, data_root_dir

import annotate

boundsFile = "bounds_dump"
DELETE_QUOTE = False

def generate_features(thread, postNum):
    dataset = Dataset('convinceme',annotation_list=['topic'])
    directory = "{}/convinceme/output_by_thread".format(data_root_dir)
    topic = dataset.discussion_annotations[int(thread)]['topic']
    discussion = dataset.load_discussion(thread)
    post = discussion.posts[int(postNum)]
    try:
       post.loadPostStruct({"site": "/convinceme", "thread": int(thread)})
       text = post.pst.text
    except:
       text = post.text.replace('\r', '')
    try:
       parent = discussion.posts[int(post.parent_id)]
       parentText = parent.text
       parentAuthor = parent.author
       parentSide = parent.side
       parentId = "<a href=\"?thread=%s&post=%s\">[see post]</a>" % (thread, post.parent_id)
    except:
       parentText = "No parent"
       parentAuthor = parentSide = parentId = ""
    author = post.author
    side = post.side
    try:
      tups = tuples[thread][postNum][:-1] #lose the last one because of an odd spurious bound
    except KeyError:
      tups = []
    for tup in tups:
        tup[-1] = tup[-1].replace(' ', '_')
    try:
      annotatedText = annotate.annotate(text, tups)
      return produceHTML(author, side, tups, parentId, parentText, parentAuthor, parentSide, annotatedText)
    except:
      pdb.set_trace()
      return ""

def produceHTML(author, side, tups, parentId, parentText, parentAuthor, parentSide, annotatedText):
    colors = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"]
    items = defaultdict(list)
    for x in tups:
        if x[-1] == "none":
           continue
        else:
           items[x[-1]].append("%d-%d" % (x[0], x[1]))
    for l in items.values():
        l.reverse()
    colorMap = dict(zip(items.keys(), colors))
    colorMap["none"] = "#7f7f7f"
    colorStyle = ""
    colorLegend = ""
    out = colorMap.items()
    out.sort(key=lambda x:x[0]) 
    for env,col in out:
        colorStyle += ".%s {background-color: %s}\n" % (env, col)
        colorLegend += """\t\t<div class="legend %s">%s<br/> %s</div>\n""" % (env, env, '<br/>'.join(items[env]))

    return """Content-Type: text/html; charset=utf-8


<html>
<head>
	<style type="text/css">
.author {color: red;}
.side {color: green;}
#text {margin: 5px; border: 1px dotted red; overflow: auto; height: 500px;}
#parentText {border: 1px dotted red; overflow: auto; height: 300px;}
#parentPost {float: left; width: 300px; margin-left: 50px;}
#post {width: 500px; float: left;}
span  {border: 1px dotted black;}
.back {color: gray; border: 1px dotted gray; font-size: x-small;}
#legend {margin-left: 50px; width: 200px; text-align: center; float: left;}
%s
	</style>
</head>
<body>
	<div id="post">
	<a href="getAllPosts.py"><span class="back">&lt;- back to list</span></a>
		<div class="author">%s</div>
		<div class="side">%s</div>
		<div id="text">%s</div>
	</div>

        <div id="legend">
%s
	</div>
	<div id="parentPost">
		<div class="author">%s %s</div>
		<div class="side">%s</div>
		<div id="parentText">%s</div>
	</div>

</body>
</html>""" % (colorStyle, author, side, annotatedText, colorLegend, parentAuthor, parentId, parentSide, parentText)

def loadTuples():
    global tuples
    svnUpdate.update()
    fin = open(boundsFile, "r")
    tuples = json.load(fin)

if  __name__ == '__main__':
    loadTuples()
    try:
      form = cgi.FieldStorage()
      thread = form.getvalue('thread')
      post = form.getvalue('post')
    except:
      thread = "1448"
      post = "12544"
    if not thread:
      thread = "1448"
      post = "42560"
    print generate_features(thread, post)
