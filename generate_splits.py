import sys
from CSVParser import CSVParser


def libsvm_entry(features, label):
    return str(label) + ' ' + ' '. \
        join(['%d: %f' % (i+1, f) for (i, f) in enumerate(features)])


def generate_training_splits(feature_file, csv_file, prefix):
    for i in range(10):
        train_folds = range(10)
        test_fold = [train_folds.pop(i)]
        fp = open('%s.train.%d.data' % (prefix, i), 'w')
        fp.write(feature_file_to_train(feature_file, train_folds,
                                       csv_file, test=False).encode('utf-8'))
        fp.close()
        fp = open('%s.test.%d.data' % (prefix, i), 'w')
        fp.write(feature_file_to_train(feature_file, test_fold,
                                       csv_file, test=True).encode('utf-8'))
        fp.close()


def feature_file_to_train(feature_file, folds,
                          csv_file='anonymized_user_manifest.csv', test=False):
    csv_data = CSVParser(csv_file)
    result = []
    features = {}
    user_ids = csv_data.get_user_ids(folds, test)
    for line in open(feature_file):
        line = line.split(',')
        user_id = line[0].strip()
        feature = [float(x.strip()) for x in line[1:]]
        features[user_id] = feature
    for user_id in user_ids:
        result.append(libsvm_entry(features[user_id],
                                   csv_data.get_label(user_id)))
    return '\n'.join(result) + '\n'


if __name__ == '__main__':
    feature_file = sys.argv[1]  # 'liwc.feature'
    csv_file = sys.argv[2]  # anonymized_user_manifest.csv
    prefix = sys.argv[3]  # 'result/liwc'
    generate_training_splits(feature_file, csv_file, prefix)
