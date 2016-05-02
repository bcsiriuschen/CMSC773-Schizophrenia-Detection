# run LDA on texts
# preprocessing steps:
import liwc_entropy as liwcEntropy
import parse_data as parse
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora
import gensim


class LdaLiwc:
    txt_data_path = '../data/txt/'
    output_path = './ldafeatures'
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
        self.tokenizer = RegexpTokenizer(r"[a-z]['a-z]*")
        self.en_stop = get_stop_words('en')
        self.p_stemmer = PorterStemmer()
        self.topicNum = 20

    def getLabelNum(self):
        userIds = parse.get_user_ids(range(10))
        self.posIdNum = sum([parse.get_label(user) for user in userIds if parse.get_label(user) == 1])
        self.negIdNum = -1 * sum([parse.get_label(user) for user in userIds if parse.get_label(user) == -1])
        print self.posIdNum, self.negIdNum

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
        stopList = self.removeStopWord(tokensList)
        print 'remove stop word'
        filterList = self.filterLIWC(stopList)
        print 'filter by LIWC'
        print filterList[0][:20]
        stemList = self.stemming(filterList)
        print 'stemming done'
        self.dictionary = corpora.Dictionary(stemList)
        print 'dictionary built'
        self.corpus = [self.dictionary.doc2bow(text) for text in stemList]
        self.ldamodel = gensim.models.ldamodel.LdaModel(self.corpus, num_topics=self.topicNum, id2word=self.dictionary, passes=20)
        print 'finished training LDA'

    def outputLDAfeature(self):
        sortedId = self.getSortedId()
        featuresList = [self.ldamodel.get_document_topics(self.corpus[documentId]) for documentId in range(len(sortedId))]
        with open(self.output_path, 'w') as file:
            for userId, features in zip(sortedId, featuresList):
                file.write(userId)
                featuresVec = [0.0 for i in range(self.topicNum)]
                for dId, feature in features:
                    featuresVec[dId] = feature
                for feature in featuresVec:
                    file.write(", "+str(feature))
                file.write("\n")

    def tokenized(self, documentList):
        tokensList = []
        for document in documentList:
            newDoc = document.lower()
            tokens = self.tokenizer.tokenize(newDoc)
            tokensList.append(tokens)
        return tokensList

    def removeStopWord(self, tokensList):
        stopList = []
        for tokens in tokensList:
            stopped_tokens = [i for i in tokens if i not in self.en_stop]
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
    print ldaliwc.ldamodel.print_topics(num_topics=20, num_words=20)
    ldaliwc.outputLDAfeature()
