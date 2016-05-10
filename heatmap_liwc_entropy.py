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
import sys


class HeatmapLiwc:
    txt_data_path = '../data/schizophrenia_txt/'
    counterCategoryList_path = './counterCategoryList'
    liwcEntropyFeatures_path = './liwcEntropyFeatures.csv'
    category_keys = ['funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe',
                     'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future',
                     'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social',
                     'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger',
                     'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain',
                     'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body',
                     'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work',
                     'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl',
                     'filler']

    def __init__(self):
        self.heatmapArray = []
        self.counterCategoryList = []
        self.calculateCounterCategoryList()
        self.heatmapEvaluation = Counter({key: 0.0 for key in self.category_keys})
        self.categoryEvaluation = Counter({key: 0.0 for key in self.category_keys})
        self.getLabelNum()

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

    def outputLiwcEntropyFeatures(self):
        sortedId = self.getSortedId()
        with open(self.liwcEntropyFeatures_path, 'w') as file:
            for idx, counterCategory in enumerate(self.counterCategoryList):
                name = sortedId[idx]
                file.write(name)
                for category in self.category_keys:
                    counter = counterCategory[category]
                    userCategoryProb = self.normalized(counter)
                    userCategoryEntropy = self.calculateEntropy(userCategoryProb)
                    file.write(','+str(userCategoryEntropy))
                file.write('\n')

    def getLabelNum(self):
        userIds = parse.get_user_ids(range(10))
        self.posIdNum = sum([parse.get_label(user) for user in userIds if parse.get_label(user) == 1])
        self.negIdNum = -1 * sum([parse.get_label(user) for user in userIds if parse.get_label(user) == -1])
        print self.posIdNum, self.negIdNum

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
        documentList = [' '.join(open('%s%s.txt' % (self.txt_data_path, user_id))) for user_id in self.getSortedId()]
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

    def calculateEntropy(self, userProb):
        entropy = 0.0
        for category, prob in userProb.iteritems():
            entropy -= prob * log(prob, 2) if prob > 0.0 else 0
        return entropy

    def calculateJensonShannonInCategory(self, heatmapType, user1Count, user2Count):
        if heatmapType in user1Count and heatmapType in user2Count:
            user1Prob = self.normalized(user1Count[heatmapType])
            user2Prob = self.normalized(user2Count[heatmapType])
            mProb = Counter({category: prob/2.0 for category, prob in (user1Prob+user2Prob).iteritems()})
            return (0.5*self.calculateKLDivergence(user1Prob, mProb) + 0.5*self.calculateKLDivergence(user2Prob, mProb))
        elif heatmapType in user1Count or heatmapType in user2Count:
            return 1.0
        else:
            return 0.0

    def calculateHeatmap(self, heatmapType='JensonShannon'):
        if heatmapType == 'overall':
            self.calculateHeatmapBy(self.calculateKLDiverenceOverall)
        elif heatmapType == 'JensonShannon':
            self.calculateHeatmapBy(self.calculateJensonShannon)
            self.evaluateCategory()
        elif heatmapType in self.category_keys:
            self.calculateHeatmapBy(lambda u1, u2: self.calculateJensonShannonInCategory(heatmapType, u1, u2))
        else:
            print 'bad use'

    def evaluateCategory(self):
        # userNormalizedList = []
        # for userCount in self.counterCategoryList:
        #     userOverall = {category: sum(counter.values()) for category, counter in userCount.iteritems()}
        #     userProb = self.normalized(userOverall)
        #     userNormalizedList.append(userProb)

        # for category in self.category_keys:
        #     self.categoryEvaluation[category] += (posneg + negpos) - (pospos + negneg)
        # TODO
        pass

    def calculateHeatmapBy(self, calMethod):
        self.heatmapArray = []
        for user1 in self.counterCategoryList:
            heatmapRow = []
            for user2 in self.counterCategoryList:
                heatmapRow.append(calMethod(user1, user2))
            self.heatmapArray.append(heatmapRow)

    def evaluateHeatmap(self, heatmapType):
        pospos = sum([sum(row[self.negIdNum:]) for row in self.heatmapArray[self.negIdNum:]])
        negneg = sum([sum(row[:self.negIdNum-1]) for row in self.heatmapArray[:self.negIdNum-1]])
        posneg = sum([sum(row[self.negIdNum:]) for row in self.heatmapArray[:self.negIdNum-1]])
        negpos = sum([sum(row[:self.negIdNum-1]) for row in self.heatmapArray[self.negIdNum:]])
        self.heatmapEvaluation[heatmapType] += (posneg + negpos) - (pospos + negneg)
        print heatmapType, (posneg + negpos) - (pospos + negneg)


if __name__ == '__main__':

    heatmap = HeatmapLiwc()
    # for category in heatmap.category_keys:
    #     heatmap.calculateHeatmap(category)
    #     heatmap.evaluateHeatmap(category)

    # print heatmap.heatmapEvaluation.most_common()
    heatmap.outputLiwcEntropyFeatures()
    # Index = heatmap.getSortedId()
    # df = DataFrame(heatmap.heatmapArray)
    # , index=Index, columns=Index)

    # plt.pcolor(df)
    # plt.yticks(np.linspace(0.5, 10.0, num=len(df.index)), df.index)
    # plt.xticks(np.linspace(0.5, 10.0, num=len(df.columns)), df.columns)
    # plt.show()
