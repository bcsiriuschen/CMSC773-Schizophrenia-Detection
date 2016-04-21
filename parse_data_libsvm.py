from parse_data_for_LIWC import get_liwc_features
from parse_data import get_label, generate_training_splits,get_user_ids

def libsvm_entry(features, label):
    return str(label) + ' ' + ' '.join(['%d: %f'%(i+1, f) for (i,f) in enumerate(features)])

def liwc_libsvm_data(folds):
    liwc_features = get_liwc_features()
    result = []
    user_ids = get_user_ids(folds)
    for user_id in user_ids:
        result.append(libsvm_entry(liwc_features[user_id], get_label(user_id)))
    return '\n'.join(result) + '\n'

if __name__ == '__main__':
    generate_training_splits(liwc_libsvm_data, 'svm/liwc')