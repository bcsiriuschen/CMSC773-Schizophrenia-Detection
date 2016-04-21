import parse_data as parse
import os

txt_data_path = '../data/txt/'

def get_liwc_features(file_name='LIWC2015_Results.csv'):
    liwc_features = {}
    for line in open(file_name).readlines()[1:]:
        user_id = line.split(',')[0].split('.')[1]
        features = [float(x) for x in line.split(',')[3:]]
        liwc_features[user_id] = features
    return liwc_features

def liwc_data(user_id):
    return '\n'.join(parse.get_tweets(user_id))

if __name__ == '__main__':
    if not os.path.exists(txt_data_path):
        os.makedirs(txt_data_path)
    user_ids = parse.get_user_ids(range(10))
    for user_id in user_ids:
        fp = open('%sliwc.%s.txt' % (txt_data_path, user_id), 'w')
        fp.write(liwc_data(user_id).encode('utf-8') + '\n')
