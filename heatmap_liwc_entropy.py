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
        self.heatmapArray = []

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

    def calculateKLDivergence(self, pProb, qProb):
        klDivergence = 0.0
        for category, prob in pProb.iteritems():
            if prob != 0.0 and qProb[category] != 0.0:
                klDivergence += prob * log(prob/qProb[category], 2)
        return klDivergence

    def calculateKLDiverenceOverall(self, user1Count, user2Count):
        # user1Count and user2Count are counterCategory
        user1Overall = {category: sum(counter.values()) for category, counter in user1Count.iteritems()}
        user2Overall = {category: sum(counter.values()) for category, counter in user2Count.iteritems()}
        user1Prob = self.normalized(user1Overall)
        user2Prob = self.normalized(user2Overall)
        return self.calculateKLDivergence(user1Prob, user2Prob)

    def calculateHeatmap(self, counterCategoryList, heatmapType='overall'):
        self.heatmapArray = []

        if heatmapType == 'overall':
            for user1 in counterCategoryList:
                heatmapRow = []
                for user2 in counterCategoryList:
                    heatmapRow.append(self.calculateKLDiverenceOverall(user1, user2))
                self.heatmapArray.append(heatmapRow)


if __name__ == '__main__':
    heatmap = HeatmapLiwc()
    documentList = heatmap.getSortedDocumentList()
    liwc = liwcEntropy.LiwcEntropy()
    counterCategoryList = [liwc.count_tokens_in_categories(document) for document in documentList]
    heatmap.calculateHeatmap(counterCategoryList, 'overall')
    Index = heatmap.getSortedId()
    df = DataFrame(heatmap.heatmapArray, index=Index, columns=Index)

    plt.pcolor(df)
    # plt.yticks(np.linspace(0.5, 10.0, num=len(df.index)), df.index)
    # plt.xticks(np.linspace(0.5, 10.0, num=len(df.columns)), df.columns)
    plt.show()
