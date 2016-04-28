# for every user's text, calculate the klDivergence of every liwc category
# use the information to generate a heatmap

import liwc_entropy as liwcEntropy
import parse_data as parse
from math import log
from collections import Counter
from pandas import DataFrame
import matplotlib.pyplot as plt
import json
import os


class HeatmapLiwc:
    txt_data_path = '../data/txt/'
    counterCategoryList_path = './counterCategoryList'

    def __init__(self):
        self.heatmapArray = []
        self.counterCategoryList = []
        self.calculateCounterCategoryList()

    def calculateCounterCategoryList(self):
        if not os.path.isfile(self.counterCategoryList_path):
            documentList = self.getSortedDocumentList()
            liwc = liwcEntropy.LiwcEntropy()
            self.counterCategoryList = [liwc.count_tokens_in_categories(document) for document in documentList]
            with open(self.counterCategoryList_path, 'w') as file:
                file.write(json.dumps(self.counterCategoryList))
        else:
            with open(self.counterCategoryList_path) as file:
                self.counterCategoryList = json.load(file)

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
        russian1 = sortedId[199]
        russian2 = sortedId[149]
        sortedId.remove(russian1)
        sortedId.remove(russian2)
        germen1 = sortedId[270]
        sortedId.remove(germen1)
        return sortedId

    def getSortedDocumentList(self):
        documentList = [' '.join(open('%sliwc.%s.txt' % (self.txt_data_path, user_id))) for user_id in self.getSortedId()]
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
        return (self.calculateKLDivergence(user1Prob, user2Prob))

    def calculateJensonShannon(self, user1Count, user2Count):
        user1Overall = {category: sum(counter.values()) for category, counter in user1Count.iteritems()}
        user2Overall = {category: sum(counter.values()) for category, counter in user2Count.iteritems()}
        user1Prob = self.normalized(user1Overall)
        user2Prob = self.normalized(user2Overall)
        mProb = Counter({category: prob/2.0 for category, prob in (user1Prob+user2Prob).iteritems()})
        return (0.5*self.calculateKLDivergence(user1Prob, mProb) + 0.5*self.calculateKLDivergence(user2Prob, mProb))

    def calculateHeatmap(self, heatmapType='overall'):
        self.heatmapArray = []

        if heatmapType == 'overall':
            for user1 in self.counterCategoryList:
                heatmapRow = []
                for user2 in self.counterCategoryList:
                    heatmapRow.append(self.calculateKLDiverenceOverall(user1, user2))
                self.heatmapArray.append(heatmapRow)
        elif heatmapType == 'JensonShannon':
            for user1 in self.counterCategoryList:
                heatmapRow = []
                for user2 in self.counterCategoryList:
                    heatmapRow.append(self.calculateJensonShannon(user1, user2))
                self.heatmapArray.append(heatmapRow)


if __name__ == '__main__':
    heatmap = HeatmapLiwc()
    heatmap.getSortedId()
    heatmap.calculateHeatmap('JensonShannon')
    # Index = heatmap.getSortedId()
    df = DataFrame(heatmap.heatmapArray)
    # , index=Index, columns=Index)

    plt.pcolor(df)
    # plt.yticks(np.linspace(0.5, 10.0, num=len(df.index)), df.index)
    # plt.xticks(np.linspace(0.5, 10.0, num=len(df.columns)), df.columns)
    plt.show()
