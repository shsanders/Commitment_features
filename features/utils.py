import re
import os
import itertools
import csv

class Generic:
    pass
simple_re = re.compile('.')

def maybe_convert(old, func = int):
    if isinstance(old, list):
        return [maybe_convert(elem, func) for elem in old]
    try:
        return func(old)
    except:
        return old

#returns a list of dicts indexed by the header (first line) in the csv file
def csv_to_dicts(filename, delimiter=None):
    if delimiter:
        csv_obj = csv.reader(open(filename),delimiter=delimiter)
    else:
        csv_obj = csv.reader(open(filename))
    csv_list = list(csv_obj)
    result_dicts = list()    
    headings = csv_list.pop(0)
    for row in csv_list:
        row_dict = dict()
        for i in range(len(headings)):
            try:
                row_dict[headings[i]] = row[i]
            except:
                row_dict[headings[i]] = None
        result_dicts.append(row_dict)
    return result_dicts

#@param csv_file: an opened file object e.g.: csv_file = open("bar.csv")
#@param dicts: an iterable (list) of dicts which contain your data. Index => Column.
#@param output_list_header: a list of column headers to use - lets you select only some from the dict, and lets you pick the order if sorting is false. If left as None, selects keys the first row in dicts
def dicts_to_csv(csv_file, dicts, include_header=True, delimiter=',', sort_by_heading=False, output_list_header=None, missing_entry_value=None):
    if output_list_header == None:
        output_list_header = dicts[0].keys()
    if sort_by_heading:
        output_list_header = sorted(output_list_header)
    output_list = list()
    if include_header:
        output_list.append(output_list_header)
    for dict_obj in dicts:
        output_list.append(list())
        for column_label in output_list_header:
            if column_label in dict_obj:
                output_list[-1].append(dict_obj[column_label])
            else:
                output_list[-1].append(missing_entry_value)
    writer = csv.writer(csv_file,delimiter=delimiter)
    for row in output_list:
        writer.writerow(row)


psutil_process_info = None
def setup_memory_management():
    import psutil
    psutil_process_info = psutil.Process(os.getpgid(0))

def running_out_of_memory():
    return (psutil_process_info.get_memory_percent() > 75.0)

# Flatten one level of nesting
def flatten(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def escape_filename(filename):
    return filename.replace('\\','_b_slash_').replace('/','_f_slash_')[:255]



#from wikipedia 
def computeKappa(mat):
    """ Computes the Kappa value
        @param n Number of rating per subjects (number of human raters)
        @param mat Matrix[subjects][categories]
        @return The Kappa value """
    n = checkEachLineCount(mat)   # PRE : every line count must be equal to n
    N = len(mat)
    k = len(mat[0])
 
    # Computing p[]
    p = [0.0] * k
    for j in xrange(k):
        p[j] = 0.0
        for i in xrange(N):
            p[j] += mat[i][j]
        p[j] /= N*n
 
    # Computing P[]    
    P = [0.0] * N
    for i in xrange(N):
        P[i] = 0.0
        for j in xrange(k):
            P[i] += mat[i][j] * mat[i][j]
        P[i] = (P[i] - n) / (n * (n - 1))
 
    # Computing Pbar
    Pbar = sum(P) / N
 
    # Computing PbarE
    PbarE = 0.0
    for pj in p:
        PbarE += pj * pj
 
    kappa = (Pbar - PbarE) / (1 - PbarE)
 
    return kappa
 
 #used for computing kappa
def checkEachLineCount(mat):
    """ Assert that each line has a constant number of ratings
        @param mat The matrix checked
        @return The number of ratings
        @throws AssertionError If lines contain different number of ratings """
    n = sum(mat[0])
 
    assert all(sum(line) == n for line in mat[1:]), "Line count != %d (n value)." % n
    return n

