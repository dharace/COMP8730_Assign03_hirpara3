# -*- coding: utf-8 -*-
"""SimlextList.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_k7Iq7BDudcAf6ZxRTcN2IkI6bS1fF5B
"""

import pandas as pd
import json
import string 
import networkx as nx
import numpy

!git clone https://github.com/dharace/COMP8730_Assign03_hirpara3.git

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/COMP8730_Assign03_hirpara3/data/SimLex-999

!ls

filePath = 'SimLex.csv'

dataFile = pd.read_csv(filePath)
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
    visited = []
    for i, w in enumerate(topWords):
        if w not in visited:
          if len(visited)<10:
            visited.append(i)
    for i in visited: 
        getWords[topWords[i]] = levels[i] 
    return getWords

jsonSimList = {}
for word in listOfAllWords:
    x = getSimilarWords(word)
    if word in x.keys():
      del x[word]
    jsonSimList[word] = x
print(jsonSimList)

"""Add Similar word list to JSON file

"""

with open('SimLexSimilar.json', 'w') as json_file:
    json.dump(jsonSimList, json_file, indent=4)