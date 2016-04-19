import re
from collections import Counter
import json


class Liwc():
    corpus_filepath = './LIWC2007_updated.trie'

    # category analysis variables:
    category_keys = ['funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe',
                     'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future',
                     'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social',
                     'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger',
                     'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain',
                     'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body',
                     'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work',
                     'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl',
                     'filler']

    def __init__(self):
        self.all_keys = self.meta_keys + self.category_keys[:-1] + self.puncuation_keys

        with open(self.corpus_filepath) as corpus_file:
            self._trie = json.load(corpus_file)

    # standard Lexicon functionality:

    def read_token(self, token, token_i=0, trie_cursor=None):
        if trie_cursor is None:
            trie_cursor = self._trie

        if '*' in trie_cursor:
            for category in trie_cursor['*']:
                yield category
        elif '$' in trie_cursor and token_i == len(token):
            for category in trie_cursor['$']:
                yield category
        elif token_i < len(token):
            letter = token[token_i]
            if letter in trie_cursor:
                for category in self.read_token(token, token_i + 1, trie_cursor[letter]):
                    yield category

    def read_document(self, document, token_pattern=r"[a-z]['a-z]*"):
        for match in re.finditer(token_pattern, document.lower()):
            for category in self.read_token(match.group(0)):
                yield category
