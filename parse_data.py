import json
import sys
import random
import re

data_path = '../data/schizophrenia/'


def parse_cvs(file_name='/anonymized_user_manifest.csv'):
    cvs_data = []
    for line in open(data_path + file_name).readlines()[1:]:
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
    tweet = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', tweet)
    tweet = re.sub(r'@[a-zA-Z0-9_]*', '', tweet)
    tweet = tweet.replace('\n', ' ')
    tweet = tweet.lower()
    # tweet = tweet.replace(':','COLON').replace('|','PIPE').replace('\n', 'NEWLINE')
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


def get_label(user_id, file_name='/anonymized_user_manifest.csv'):
    cvs_data = parse_cvs(file_name)
    for entry in cvs_data:
        if entry['user_id'] == user_id:
            return entry['label']
    return None


def get_user_ids(folds, file_name='/anonymized_user_manifest.csv'):
    result = []
    cvs_data = parse_cvs(file_name)
    for entry in cvs_data:
        if entry['fold'] in folds:
            result.append(entry['user_id'])
    return result


def vw_data(folds, num_tweets=50):
    result = []
    user_ids = get_user_ids(folds)
    for user_id in user_ids:
        result.append(vw_entry(get_tweets(user_id, num_tweets), get_label(user_id)))
    return '\n'.join(result) + '\n'
