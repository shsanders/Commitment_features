from collections import Counter

def get_ngrams(feature_vector, words, n=1, prefix='uni_'):
    unigrams = ['-nil-' for i in range(n-1)]+words+['-nil-' for i in range(n-1)]
    n_grams = list()
    for i in range(len(unigrams)-n+1):
        n_grams.append(' '.join(unigrams[i:i+n]))
    word_counts = Counter(n_grams)
    total_words = len(n_grams)
    for word, count in word_counts.items():
        feature_vector[prefix+word]=True
