
data = './LIWC2015_Results.csv'


def parse_liwc_cvs():
    labels = open(data).readlines()[0].split(',')
    features = []
    for line in open(data).readlines()[1:]:
        data_entry = {}
        data_entry['user_id'] = line.split(',')[0].split('.')[1]
        for id, label in enumerate(labels[1:]):
            data_entry[label] = float(line.split(',')[id+1])

        features.append(data_entry)
    return features

if __name__ == '__main__':
    features = parse_liwc_cvs()
