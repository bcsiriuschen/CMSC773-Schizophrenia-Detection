# run LDA on texts
# preprocessing steps:
import liwc_entropy as liwcEntropy
import parse_data as parse
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
import re


class LdaLiwc:
    txt_data_path = '../data/txt/'
    output_path = './ldafeatures.csv'
    output_path2 = './ldafeatures2.csv'
    mylist = ['just', 'via', 'make', 'can', 'amp', 'get']

    def __init__(self):
        self.tokenizer = RegexpTokenizer(r"[@a-z0-9]['a-z0-9]*")
        self.p_stemmer = PorterStemmer()
        self.en_stop = [self.p_stemmer.stem(i) for i in get_stop_words('en')]
        self.topicNum = 20

    def getSortedId(self):
        userIds = parse.get_user_ids(range(10))
        sortedId = sorted(userIds, key=lambda user: parse.get_label(user))
        return sortedId

    def getSortedDocumentList(self):
        documentList = [' '.join(open('%sliwc.%s.txt' % (self.txt_data_path, user_id))) for user_id in self.getSortedId()]
        return documentList

    def runLDA(self):
        documentList = self.getSortedDocumentList()
        print 'document loaded'

        tokensList = self.tokenized(documentList)
        print 'tokenized'

        filterList = self.preprocessing(tokensList)

        self.dictionary = corpora.Dictionary(filterList)
        print 'dictionary built'

        self.corpus = [self.dictionary.doc2bow(text) for text in filterList]
        # self.tfidf = models.TfidfModel(self.corpus)
        # print 'using tfidf'

        self.ldamodel = gensim.models.ldamodel.LdaModel(self.corpus, num_topics=self.topicNum, id2word=self.dictionary, passes=20)
        print 'finished training LDA'

    def preprocessing(self, tokensList):
        # filterList = self.filterLIWC(tokensList)
        # print 'filter by LIWC'
        # print filterList[0][:20]
        tokensList = self.stemming(tokensList)
        print 'stemming done'
        tokensList = self.removeStopWord(tokensList)
        print 'stop word removed'
        print tokensList[5][:50]
        print tokensList[20][:50]
        return tokensList

    def outputLDAfeature(self):
        sortedId = self.getSortedId()
        # featuresList = [self.ldamodel.get_document_topics(self.tfidf[self.corpus[documentId]]) for documentId in range(len(sortedId))]
        # with open(self.output_path, 'w') as file:
        #     for userId, features in zip(sortedId, featuresList):
        #         file.write(userId)
        #         featuresVec = [0 for i in range(self.topicNum)]
        #         for dId, feature in features:
        #             featuresVec[dId] = feature
        #         for feature in featuresVec:
        #             file.write(", "+str(feature))
        #         file.write("\n")
        featuresList = [self.ldamodel.get_document_topics(self.corpus[documentId]) for documentId in range(len(sortedId))]
        with open(self.output_path, 'w') as file:
            for userId, features in zip(sortedId, featuresList):
                file.write(userId)
                featuresVec = [0 for i in range(self.topicNum)]
                for dId, feature in features:
                    featuresVec[dId] = feature
                for feature in featuresVec:
                    file.write(", "+str(feature))
                file.write("\n")

    def tokenized(self, documentList):
        tokensList = []
        for document in documentList:
            # remove all http and newline and colon
            document = re.sub('COLON', ':', document)
            document = re.sub('NEWLINE', ' ', document)
            document = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', document)
            document = re.sub(r'@[a-zA-Z0-9_]*', '', document)
            newDoc = document.lower()
            tokens = self.tokenizer.tokenize(newDoc)
            tokensList.append(tokens)
        return tokensList

    def removeStopWord(self, tokensList):
        stopList = []
        for tokens in tokensList:
            stopped_tokens = [i for i in tokens if
                              i not in self.en_stop and
                              len(i) >= 3 and
                              i not in self.mylist]
            stopList.append(stopped_tokens)
        return stopList

    def filterLIWC(self, tokensList):
        filterList = []
        liwc = liwcEntropy.LiwcEntropy()
        for tokens in tokensList:
            filterTokens = []
            for token in tokens:
                for category in liwc.read_token(token):
                    filterTokens.append(category[0])
                    break
            filterList.append(filterTokens)
        return filterList

    def stemming(self, tokensList):
        stemList = []
        for tokens in tokensList:
            stemmed_tokens = [self.p_stemmer.stem(i) for i in tokens]
            stemList.append(stemmed_tokens)
        return stemList

if __name__ == '__main__':
    ldaliwc = LdaLiwc()
    ldaliwc.runLDA()
    print ldaliwc.ldamodel.print_topics(num_topics=ldaliwc.topicNum, num_words=20)
    ldaliwc.outputLDAfeature()
