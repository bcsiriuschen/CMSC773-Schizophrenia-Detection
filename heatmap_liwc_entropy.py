# for every user's text, calculate the entropy of every liwc category
# use the information to generate a heatmap

import liwc_entropy as liwcEntropy
import parse_data as parse
from math import log
from collections import Counter
from pandas import DataFrame
import matplotlib.pyplot as plt

txt_data_path = '../data/txt/'


class HeatmapLiwc:

    def __init__(self):
        pass

    def normalized(self, counterIn):
        counter = Counter(counterIn)
        total = sum(counter.values(), 0.0)
        if total != 0.0:
            for key in counter:
                counter[key] /= total
        return counter

    def getSortedId(self):
        userIds = parse.get_user_ids(range(10))
        sortedId = sorted(userIds, key=lambda user: parse.get_label(user))
        return sortedId

    def getSortedDocumentList(self):
        documentList = [' '.join(open('%sliwc.%s.txt' % (txt_data_path, user_id))) for user_id in self.getSortedId()]
        return documentList

    def normalizedCategory(self, counterCategory):
        normalCategory = {}
        for category, counter in counterCategory.iteritems():
            normalCategory[category] = self.normalized(counter)
        return counterCategory

    def getEntropy(self, counter):
        # assume normalized
        entropy = 0.0
        for value in counter.values():
            if value != 0.0:
                entropy -= value * log(value, 2)
        return entropy

    def calculateScore(self, user1, user2):
        sum = 0.0
        for category, entropy in user1.iteritems():
            sum += abs(entropy - user2[category])
        return log(sum+1)

    def calculateKLDivergence(self, user1Prob, user2Prob):
        pass

    def calculateKLDiverenceOverall(self, user1Count, user2Count):
        # user1Count and user2Count are counterCategory
        user1Overall = {category: sum(counter.values()) for category, counter in user1Count.iteritems()}
        user2Overall = {category: sum(counter.values()) for category, counter in user2Count.iteritems()}
        user1Prob = self.normalized(user1Overall)
        user2Prob = self.normalized(user2Overall)
        return self.calculateKLDivergence(user1Prob, user2Prob)

    def getHeatmap(self, counterCategoryList):
        heatmapArray = []
        categoryEntropyList = []

        for counterCategory in counterCategoryList:
            counterCategory = self.normalizedCategory(counterCategory)
            categoryEntropy = {}
            for category, counter in counterCategory.iteritems():
                categoryEntropy[category] = self.getEntropy(counter)
            categoryEntropyList.append(categoryEntropy)

        for user1 in categoryEntropyList:
            heatmapRow = []
            for user2 in categoryEntropyList:
                heatmapRow.append(self.calculateScore(user1, user2))
            heatmapArray.append(heatmapRow)

        return heatmapArray

if __name__ == '__main__':
    documentList = getSortedDocumentList()
    liwc = liwcEntropy.LiwcEntropy()
    counterCategoryList = [liwc.count_tokens_in_categories(document) for document in documentList]
    heatmapArray = getHeatmap(counterCategoryList)
    Index = getSortedId()
    df = DataFrame(heatmapArray, index=Index, columns=Index)

    plt.pcolor(df)
    # plt.yticks(np.linspace(0.5, 10.0, num=len(df.index)), df.index)
    # plt.xticks(np.linspace(0.5, 10.0, num=len(df.columns)), df.columns)
    plt.show()
