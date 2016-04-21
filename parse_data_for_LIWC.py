import parse_data as parse
import os

txt_data_path = '../data/txt/'


def liwc_data(user_id):
    return '\n'.join(parse.get_tweets(user_id))

if __name__ == '__main__':
    if not os.path.exists(txt_data_path):
        os.makedirs(txt_data_path)
    user_ids = parse.get_user_ids(range(10))
    for user_id in user_ids:
        fp = open('%sliwc.%s.txt' % (txt_data_path, user_id), 'w')
        fp.write(liwc_data(user_id).encode('utf-8') + '\n')
