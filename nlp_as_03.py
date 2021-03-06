!pip install pytrec_eval
!pip install contractions
!pip install gensim

import pytrec_eval
import pandas as pd
import numpy as np
import json
import os
from os import listdir
from os.path import isfile, join
import csv
import nltk
from nltk.corpus import brown, reuters, gutenberg
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LinearRegression
import contractions
import string
import gensim
from gensim.models import Word2Vec

!git clone https://github.com/dharace/COMP8730_Assign03_hirpara3.git

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/COMP8730_Assign03_hirpara3

!ls

"""**Find similarity words using SimLex-999 dataset**"""

nltk.download('gutenberg')
nltk.download('punkt')
nltk.download('brown')

dataFile = pd.read_csv('data/SimLex-999/SimLex.csv')
dataFile.head(5)

listOfAllWords = dataFile.word1.tolist()
for i,v in enumerate(dataFile.word2.tolist()):
    listOfAllWords.insert(2*i+1,v)
print(listOfAllWords)

listOfSimLexWords = list(set(listOfAllWords))
print(listOfSimLexWords)

def findWords(word):
    temp = [i for i, x in enumerate(listOfAllWords) if x == word]
    result = []
    for i in temp:
      result.append(listOfAllWords[i+1] if i%2 == 0 else listOfAllWords[i-1])
    return result

def getSimilarWords(word):
    getWords = {}
    topWords = findWords(word)
    max = 10
    levels = [max]*len(topWords)
    for i, w in enumerate(topWords):
        max -= 1
        if i > 10:
            break
        if len(set(topWords))<=10:
            topWords.extend(findWords(w))
            levels.extend([max]*len(findWords(w)))
        else:
            break
    visitedWords = []
    for i, w in enumerate(topWords):
        if w not in visitedWords:
          if len(visitedWords)<10:
            visitedWords.append(i)
    for i in visitedWords: 
        getWords[topWords[i]] = levels[i] 
    return getWords

jsonSimList = {}
for word in listOfAllWords:
    x = getSimilarWords(word)
    if word in x.keys():
      del x[word]
    jsonSimList[word] = x
print(jsonSimList)

""" **Tf-iDF using *Gutenberg* and *Brown* corpus**"""

def processWords(word):
    # lower case word
    word = word.lower()
    # fix contractions
    text = contractions.fix(word)
    # remove punctuations
    text = text.translate(str.maketrans('', '', string.punctuation)) # removing punctuations
    # replace @
    text = text.replace('@', '') 
    return text

def processList(inputlist):
  result = []
  for sentence in inputlist:
    sentence = ' '.join(sentence)
    sentence = processWords(sentence)
    result.append(sentence)
  return result

brownWords = processList(brown.sents())

gutenbergWords = processList(gutenberg.sents('austen-emma.txt'))

# def wordToTfIdf(words, filePath):
def wordToTfIdf(words):
  countVectorizer = CountVectorizer()
  tfidfTransformer = TfidfTransformer()
  tfidfMatrix = tfidfTransformer.fit_transform(countVectorizer.fit_transform(words))
  wordToTfidf = dict(zip(countVectorizer.get_feature_names(), tfidfTransformer.idf_))
#  saveResultToJson(wordToTfidf, filePath)
  return wordToTfidf

brownWordsJsonTfiDF = wordToTfIdf(brownWords)
brownWordsJsonTfiDF

gutenbergWordsJsonTfiDF = wordToTfIdf(gutenbergWords)
gutenbergWordsJsonTfiDF

words = list(brownWordsJsonTfiDF.keys())
values = list(brownWordsJsonTfiDF.values())

jsonSimList = {}
for word in listOfAllWords:
    x = getSimilarWords(word)
    if word in x.keys():
      del x[word]
    jsonSimList[word] = x
print(jsonSimList)

resDict = {}
for w in listOfAllWords:
    df = pd.DataFrame({'words':words, 'values':values})
    if w in words:
        id = words.index(w)
        df['sim'] = df['values'].apply(lambda x: abs(x-values[id]))
        df.sort_values('sim')
        x = df['words'][:10].to_list()
        y = df['values'][:10].to_list()
        z = {}
        for i, word in enumerate(x):
          z[word] = y[i]
        resDict[w] = z
    else:
        resDict[w] = []
resDict

"""**Word2Vec find similarity **"""

window_size = [1, 2, 5, 10]
vector_size = [10, 50, 100, 300]

def buildWord2VecModel(words, fileName):
  for ws in window_size:
    for vs in vector_size:
        word2vecModel = gensim.models.Word2Vec(window=ws, size=vs, workers=5)
        word2vecModel.build_vocab(words)
        # epochs = 1000 takes lot of time to run, reducing this to 10 easily works for testing
        word2vecModel.train(words, total_examples=word2vecModel.corpus_count, epochs=10) 
        word2vecModel.save(fileName + str(ws) + 'VS' + str(vs).format(ws,vs))

buildWord2VecModel(gutenbergWords, 'data/Word2Vec/Guternberg/GutenW2V_WS')

buildWord2VecModel(brownWords, 'data/Word2Vec/Brown/BrownW2V_WS')

gutenFiles = [f for f in listdir('data/Word2Vec/Guternberg') if isfile(join('data/Word2Vec/Guternberg', f))]
gutenFiles

brownFiles = [f for f in listdir('data/Word2Vec/Brown') if isfile(join('data/Word2Vec/Brown', f))]
brownFiles

simWords = []
for k,v in jsonSimList.items():
    simWords.append(v)
print(simWords)

def getData(files, fName, path):
  getAllJson = []
  for file in files:
      vect = Word2Vec.load(path + file)
      result = {}
      for i, w in enumerate(listOfSimLexWords):
          try: 
              x = vect.wv.most_similar(w, 10)
          except:
              x = []
          final_words = [m[0] for m in x]
          temp = {}
          for word in simWords[i]:
              if word in final_words:
                  id = final_words.index(word)
                  if id in range(0,3):
                      id2rank = 5
                  elif id in range(3,7):
                      id2rank = 4
                  elif id in range(7,10):
                      id2rank = 3
                  temp[word] = id2rank
              else:
                  temp[word] = 0
          result[w] = temp
      getAllJson.append(result)
  return getAllJson  
              
      # with open(fName.format(f), 'w') as fp:
      #     json.dump(result, fp, indent=4)

gutenWordsJsonW2V = getData(gutenFiles, 'Guternbeg.json', 'data/Word2Vec/Guternberg/')
gutenWordsJsonW2V

brownWordsJsonW2V = getData(brownFiles, 'Brown.json', 'data/Word2Vec/Brown/')
brownWordsJsonW2V

def getNdcgScoreW2V(files, jsonWords):
  for i, model in enumerate(files):
    temp = jsonWords[i]
    evaluator = pytrec_eval.RelevanceEvaluator(
        jsonSimList, {'ndcg'})

    x = evaluator.evaluate(temp)
    score= []
    for i in x.items():
        score.append((i[1]['ndcg']))

    print("Model " , model, ",", sum(score)/len(score))

getNdcgScoreW2V(gutenFiles, gutenWordsJsonW2V)

getNdcgScoreW2V(brownFiles, brownWordsJsonW2V)
