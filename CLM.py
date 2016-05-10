from parse_data import *

class CLM:

    def __init__(self, data="", n=5):
        self.model = {}
        self.n = n
        self.train(data)

    def train(self, data):
        corpus = self.string2cngram(data, self.n)
        for ngram in corpus:
            head = ngram[:-1]
            tail = ngram[-1]
            if head not in self.model:
                self.model[head] = {}
                self.model[head]['count'] = 0
            if tail not in self.model[head]:
                self.model[head][tail] = 0
            self.model[head][tail] += 1
            self.model[head]['count'] += 1

    def predict_word(self, ngram):
        head = ngram[:-1]
        tail = ngram[-1]
        if head not in self.model:
            return 0
        if tail not in self.model[head]:
            return 0
        return float(self.model[head][tail])/self.model[head]['count']

    def predict_text(self, text):
        corpus = self.string2cngram(text)
        score = 0
        for word in corpus:
            score += self.predict_word(word)
        return float(score)/len(corpus)

    def print_model(self):
        print self.model

    @staticmethod
    def string2cngram(s, n=5):
        return [s[i:i+n] for i in range(len(s)-n+1)]

    @staticmethod
    def string2charList(s):
        return [c for c in s]


def get_group_tweets(folds, label, n=100):
    result = []
    user_ids = get_user_ids(folds)
    for user_id in user_ids:
        if get_label(user_id) == label:
            result.extend(get_tweets(user_id, n))
    return '$$$$'.join(result)


def CLM_feature():
    fp = open('clm.feature', 'w')
    for i in range(10):
        print 'Training Fold %d' % (i)
        train_folds = range(10)
        test_fold = [train_folds.pop(i)]
        schizo_tweets = get_group_tweets(train_folds, 1, -1)
        control_tweets = get_group_tweets(train_folds, -1, -1)
        control_CLM = CLM(control_tweets)
        schizo_CLM = CLM(schizo_tweets)
        print 'Testing...'
        for user_id in get_user_ids(test_fold):
            fp.write('%s,' % (user_id))
            tweets = get_tweets(user_id)
            max_score = 0
            while (len(tweets) > 0):
                score = 0
                text = '$$$$'.join(tweets[:50])
                tweets = tweets[50:]
                '''
                control_score = control_CLM.predict_text(text)
                schizo_score = schizo_CLM.predict_text(text)
                fp.write('%.4f, %.4f\n' % (control_score, schizo_score))
                '''
                cngram = CLM.string2cngram(text)
                for word in cngram:
                    if schizo_CLM.predict_word(word) > control_CLM.predict_word(word):
                        score += 1
                curr_score = float(score)/len(cngram)
                if curr_score > max_score:
                    max_score = curr_score
            fp.write('%.4f\n' % (float(max_score)))

if __name__ == '__main__':
    CLM_feature()
