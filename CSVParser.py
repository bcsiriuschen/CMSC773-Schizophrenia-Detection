class CSVParser:

    def __init__(self, file_name):
        self.cvs_data = []
        self.label = {}
        for line in open(file_name).readlines()[1:]:
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
            data_entry['train_only'] = int(line.split(',')[6])
            self.cvs_data.append(data_entry)
            self.label[data_entry['user_id']] = data_entry['label']

    def get_user_ids(self, folds, test=False):
        result = []
        for entry in self.cvs_data:
            if test is True and entry['train_only'] == 1:
                continue
            if entry['fold'] in folds:
                result.append(entry['user_id'])
        return result

    def get_label(self, user_id):
        return self.label[user_id]
