import re
import json


class DataParser:

    def __init__(self, data_path, csv_filename):
        self.data_path = data_path
        self.label = {}
        self.fold = {}
        self.tweets = {}

        self.user_ids_from_fold = {}
        self.user_ids_from_label = {}
        for i in range(1,11):
            self.user_ids_from_fold[i] = []
            self.user_ids_from_fold[-i] = []
        self.user_ids_from_label[1] = []
        self.user_ids_from_label[-1] = []

        for line in open(csv_filename).readlines()[1:]:
            user_id = line.split(',')[0].strip()
            label = line.split(',')[1]
            if line.split(',')[1] == 'schizophrenia':
                label = 1
            else:
                label = -1
            fold = int(line.split(',')[5]) + 1
            self.label[user_id] = label
            self.fold[user_id] = fold
            self.user_ids_from_label[label].append(user_id)
            for i in range(1, 11):
                if i == fold:
                    self.user_ids_from_fold[i].append(user_id)
                else:
                    self.user_ids_from_fold[-i].append(user_id)

    def get_label(self, user_id):
        return self.label[user_id]

    def get_fold(self, user_id):
        return self.fold[user_id]

    def get_tweets(self, user_id, ext='tweets'):
        if self.tweets.get(user_id) is None:
            result = []
            tweets = open('%s/%s.%s' % (self.data_path, user_id, ext)) \
                .readlines()
            for tweet in tweets:
                tweet_data = json.loads(tweet)
                if not tweet_data['text'].startswith('RT'):
                    result.append(self.preprocess_tweet(tweet_data['text']))
            self.tweets[user_id] = result

        return self.tweets[user_id]

    def get_tweets_by_label(self, label):
        result = []
        user_ids = self.user_ids_from_label[label]
        for user_id in user_ids:
            result.extend(self.get_tweets(user_id))
        return result

    def get_tweets_by_fold(self, fold):
        result = []
        user_ids = self.user_ids_from_fold[fold]
        for user_id in user_ids:
            result.extend(self.get_tweets(user_id))
        return result

    @staticmethod
    def preprocess_tweet(tweet):
        tweet = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]| \
            (?:%[0-9a-fA-F][0-9a-fA-F]))+', '', tweet)
        tweet = re.sub(r'@[a-zA-Z0-9_]*', '', tweet)
        tweet = tweet.replace('\n', ' ')
        tweet = tweet.replace(':', 'COLON').replace('|', 'PIPE')
        tweet = tweet.replace('schizophrenia', '')
        tweet = tweet.replace('schizo', '')
        tweet = tweet.replace('skitzo', '')
        tweet = tweet.replace('skitso', '')
        tweet = tweet.replace('schizotypal', '')
        tweet = tweet.replace('schizoid', '')
        tweet = tweet.lower()
        return tweet

if __name__ == '__main__':
    dp = DataParser('../data/schizophrenia/',
                    '../data/schizophrenia/anonymized_user_manifest.csv')

    tweets = dp.get_tweets('_UqnfSjiEX')
    for t in tweets:
        print t
