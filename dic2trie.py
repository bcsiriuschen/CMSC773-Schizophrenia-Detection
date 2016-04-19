# This file turn ./LIWC2007_updated.dic to a jason file that is easy to search
import json

categories = {}
trie = {}
corpus_filepath = './LIWC2007_updated.dic'


def add(key, categories):
    cursor = trie
    for letter in key:
        if letter == '*':
            cursor['*'] = categories
            break
        if letter not in cursor:
            cursor[letter] = {}
        cursor = cursor[letter]
    cursor['$'] = categories


def dic2trie():
    for line in open(corpus_filepath).readlines():
        if not line.startswith('%'):
            parts = line.strip().split('\t')
            if parts[0].isdigit():
                # cache category names
                categories[parts[0]] = parts[1]
            else:
                # print parts[0], ':', parts[1:]
                add(parts[0], [categories[category_id] for category_id in parts[1:]])

    fp = open('./LIWC2007_updated.trie', 'w')
    fp.write(json.dumps(trie, sort_keys=True))

# indent=4,
if __name__ == '__main__':
    dic2trie()
