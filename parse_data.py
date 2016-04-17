import json
import sys
import random

data_path = '../data/schizophrenia/'


def parse_cvs():
    cvs_data = []
    for line in open(data_path + '/anonymized_user_manifest.csv').readlines()[1:]:
        data_entry = {}
        data_entry['user_id'] = line.split(',')[0]
        if line.split(',')[1] == 'schizophrenia':
            data_entry['label'] = 1
        else:
            data_entry['label'] = -1
        data_entry['age'] = float(line.split(',')[2])
        data_entry['gender'] = line.split(',')[3]
        data_entry['num_tweets'] = int(line.split(',')[4])
        data_entry['fold'] = int(line.split(',')[5])
        cvs_data.append(data_entry)
    return cvs_data


def preprocess_tweet(tweet):
    tweet = tweet.replace(':','COLON').replace('|','PIPE').replace('\n', 'NEWLINE')
    tweet = ' '.join([x for x in tweet.split(' ') if not x.startswith('httpCOLON//')])
    return tweet


def get_tweets(user_id, num_tweets=-1):
    result = []
    tweets = open('%s/%s.tweets' % (data_path, user_id)).readlines()
    count = 0
    for tweet in tweets:
        tweet_data = json.loads(tweet)
        if not tweet_data['text'].startswith('RT'):
            result.append(preprocess_tweet(tweet_data['text']))
            count += 1
        if count == num_tweets:
            break
    return result


def get_label(user_id):
    cvs_data = parse_cvs()
    for entry in cvs_data:
        if entry['user_id'] == user_id:
            return entry['label']
    return None


def get_user_ids(folds):
    result = []
    cvs_data = parse_cvs()
    for entry in cvs_data:
        if entry['fold'] in folds:
            result.append(entry['user_id'])
    return result


def vw_entry(tweets, label):
    if label > 0:
        return '+1 | %s' % (' '.join(tweets))
    else:
        return '-1 | %s' % (' '.join(tweets))


def vw_data(folds, num_tweets=50):
    result = []
    user_ids = get_user_ids(folds)
    for user_id in user_ids:
        result.append(vw_entry(get_tweets(user_id, num_tweets), get_label(user_id)))
    random.shuffle(result)
    return '\n'.join(result)

if __name__ == '__main__':
    for i in range(10):
        fp = open('vw.%d.data' % (i), 'w')
        fp.write(vw_data([i], 100).encode('utf-8') + '\n')
