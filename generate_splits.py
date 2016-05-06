import sys
from parse_data import *


def libsvm_entry(features, label):
    return str(label) + ' ' + ' '. \
        join(['%d: %f' % (i+1, f) for (i, f) in enumerate(features)])


def vw_entry(features, label):
    if label > 0:
        return '+1 | %f' % (' '.join(features))
    else:
        return '-1 | %f' % (' '.join(features))


def generate_training_splits(func, prefix):
    for i in range(10):
        train_folds = range(10)
        test_fold = [train_folds.pop(i)]
        fp = open('%s.train.%d.data' % (prefix, i), 'w')
        fp.write(func(train_folds).encode('utf-8'))
        fp.close()
        fp = open('%s.test.%d.data' % (prefix, i), 'w')
        fp.write(func(test_fold).encode('utf-8'))
        fp.close()


def feature_file_to_train(feature_file, folds, format_type='svm'):
    result = []
    features = {}
    user_ids = get_user_ids(folds)
    for line in open(feature_file):
        line = line.split(',')
        user_id = line[0].strip()
        feature = [float(x.strip()) for x in line[1:]]
        features[user_id] = feature
    for user_id in user_ids:
        if format_type == 'svm':
            result.append(libsvm_entry(features[user_id], get_label(user_id)))
        else:
            result.append(vw_entry(features[user_id], get_label(user_id)))
    return '\n'.join(result) + '\n'


if __name__ == '__main__':
    file_name = sys.argv[1]  # 'liwc.feature'
    prefix = sys.argv[2]  # 'svm/liwc'
    format_type = sys.argv[3]
    f = lambda folds: feature_file_to_train(file_name, folds, format_type)
    generate_training_splits(f, prefix)
    # generate_training_splits(lambda folds:get_group_tweets(folds, 1), 'tweets/schizo')
