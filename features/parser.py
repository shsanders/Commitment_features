# -*- coding: utf-8 -*-

import re
import string

import nltk.tokenize

newline_replacements = (re.compile(r'[\x0A\x0C\x0D]'), '\x0A')
punctuation = re.compile('^['+re.escape(string.punctuation)+']+$')

spaces_re = re.compile(r'\s+', re.UNICODE | re.DOTALL)
legal_tokens = [spaces_re, #whitespace
                re.compile(r"[a-zA-Z]+$", re.UNICODE), #words
                re.compile(r"[a-zA-Z]+([ʼ’ʻ`'\-]\w+)*$", re.UNICODE), #words and word-like things
                re.compile(r"\$?\d+((\.|,)\d+)*$", re.UNICODE), #basic numbers, ipv4 addresses, etc
                re.compile(r'\d{1,2}/\d{1,2}(/\d{2,4})?$', re.UNICODE), #date
                re.compile(r'\d+(\.\d+)?[%°]$', re.UNICODE), #80% or 80°
                re.compile(r'\d+\'s$', re.UNICODE), #80's 
                re.compile(r'\d*(1st|2nd|3rd|[04-9]th)$', re.UNICODE | re.IGNORECASE), #80th, 1st, 81st, etc
                re.compile(r'(#|0x|\\x)?[a-fA-F0-9]+$'), #hex
                re.compile(r'[!?]+$'), #!?!
                re.compile('(['+re.escape(string.punctuation)+'])\\1+$'), #same punctuation character repeated ....... && *******
                re.compile(r'[}>\]<]?[:;=8BxX][\'`]?[oc\-]?[*XxO03DPpb)[\]}|/\\(]$'), #Western emoticons - see: http://en.wikipedia.org/wiki/List_of_emoticons
                re.compile(r'[(=]?[\-~^T0oOxX\'<>.,\'][_\-.][\-~^T0oOxX\'<>.,\'][)=]?$'), #Eastern emoticons
                re.compile(r'<[/\\]?3+$'), #heart <3
                re.compile(r'\(( ?[.oO] ?)(\)\(|Y)\1\)$'), #boobs
                re.compile(r"[a-zA-Z]+\*+[a-zA-Z]*$", re.UNICODE), #w***s
                re.compile(r'[@#$%^&*]+$', re.UNICODE), # @$%# symbols
                re.compile(r'&[a-zA-Z]+;$', re.UNICODE), #html escapes
                re.compile(r'&#\d+;$', re.UNICODE), #html escapes
                re.compile(r'(https?://|www\.).*$', re.UNICODE | re.IGNORECASE), # urls
                re.compile(r'.*\.(edu|com|org|gov)/?$', re.UNICODE | re.IGNORECASE), # more urls and emails
                re.compile(r'\x00+$', re.UNICODE) # null characters
                ]
#given english text, returns a list of tokens or a  list of lists of tokens if told to break_into_sentences
def tokenize(text, break_into_sentences = False, leave_whitespace=False):
    token_spans = list()
    previous_end = 0
    for iter in spaces_re.finditer(text):
        if iter.start()!=0:
            token_spans.append((previous_end, iter.start()))
        token_spans.append((iter.start(),iter.end()))
        previous_end = iter.end()
    if previous_end != len(text):
        token_spans.append((previous_end, len(text)))
    
    tokens = [text[start:end] for (start,end) in token_spans]
    tokens = reduce(lambda x, y: x+y, map(tokenize_word, tokens), [])
    if break_into_sentences:
        tokens = tokens_to_sentences(tokens)
    if not leave_whitespace:
        tokens = remove_whitespace_tokens(tokens, break_into_sentences)
    return tokens

#greedily splits into largest possible tokens
def tokenize_word(word):
    if is_legal_token(word):
        return [word]
    tokens = list()
    for i in range(len(word),0,-1):
        if is_legal_token(word[:i]):
            tokens.append(word[:i])
            tokens.extend(tokenize_word(word[i:]))
            break
        if is_legal_token(word[len(word)-i:]):
            tokens.extend(tokenize_word(word[:len(word)-i]))
            tokens.append(word[len(word)-i:])
            break
    return tokens
        
def is_legal_token(token):
    if len(token) == 1:
        return True
    for regex in legal_tokens:
        if regex.match(token):
            return True
    return False
    
def sentences(text):
    return nltk.tokenize.sent_tokenize(text) #nltk's is actually pretty good, albeit unpredictable

#TODO - once people upgrade nltk, use nltk's span option for sent tokenizing...
def tokens_to_sentences(tokens):
    sentences = list()
    sentence_buffer = list()
    for token in tokens:
        if len(token) == 0 or '\n' in token or token[-1] in ['.','?',':','!',';'] or '\0' in token:
            sentence_buffer.append(token)
            sentences.append(sentence_buffer)
            sentence_buffer = list()
        else:
            sentence_buffer.append(token)
    if len(sentence_buffer) > 0:
        sentences.append(sentence_buffer)
    return sentences

#Note: catches all that start with whitespace
def remove_whitespace_tokens(tokens, sentences = False):
    if sentences:
        for i in range(len(tokens)):
            tokens[i] = remove_whitespace_tokens(tokens[i]) # tokens[i] is a sentence
        return tokens

    return [token for token in tokens if not spaces_re.match(token)]
        
#borrowed from nltk w/ modifications
clean_html_regexes = [(re.compile(r"(?is)<(script|style).*?>.*?(</\1>)"), ""),
                     (re.compile(r"(?s)<!--(.*?)-->[\n]?", re.DOTALL), ""),
                     (re.compile(r'(?i)<(b|h)r */? *>'), '\n'),
                     (re.compile(r'(?s)<.*?>'), '')]
def clean_html(text):
    for regex, sub in clean_html_regexes:
        text = regex.sub(sub, text)
    text = replace_html_escapes(text)
    text = text.replace('  ',' ').replace('  ',' ')
    return text

#see: http://www.theukwebdesigncompany.com/articles/entity-escape-characters.php
#and: http://www.fileformat.info/info/unicode/char/201d/index.htm
#  ('&amp;','&') purposely left out - replace on own
html_escapes = [('&nbsp;',' '),
                ('&quot;','"'),
                ('&lt;','<'),
                ('&gt;','>')]
html_escapes_regexes = [(re.compile(r'&(l|r)dquo;', re.IGNORECASE), '"'),
                        (re.compile(r'&(l|r)squo;', re.IGNORECASE), "'"),
                        (re.compile(r'&acute;', re.IGNORECASE), "'")]
lossy_html_escape_regexes = [(re.compile(r'&(A|E|I|O|U|a|e|i|o|u|N|n|Y|y)(grave|acute|circ|tilde|uml|ring);'), r'\1')]

def replace_html_escapes(text, replace_amp = False, use_lossy_escapes = True):
    for original, sub in html_escapes:
        text = text.replace(original, sub)
    for regex, sub in html_escapes_regexes:
        text = regex.sub(sub, text)
    if use_lossy_escapes:
        for regex, sub in lossy_html_escape_regexes:
            text = regex.sub(sub, text)
    if replace_amp:
        text = text.replace('&amp;','&')
    return text

#one or both of text and term can also be lists of tokens, this speeds things up immensely 
def is_text_initial(term, text, start_within=5, ignore_case=True):
    if type(term) != type(list()):
        if ignore_case: term = term.lower()
        term_tokens = tokenize(term)
    else:
        term_tokens = [token.lower() for token in term] if ignore_case else term
    if type(text) != type(list()):
        if ignore_case: text = text.lower()
        text_tokens = tokenize(text)
    else:
        text_tokens = [token.lower() for token in text] if ignore_case else text
    spacey_text = ' '+(' '.join(text_tokens[:start_within-1+len(term_tokens)]))+' '
    spacey_term = ' '+(' '.join(term_tokens))+' '
    return spacey_term in spacey_text
