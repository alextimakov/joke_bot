# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## MultinomialNB

# ### В качестве baseline модели был выбран Multinomial Naive Bayes в реализации scikit-learn
# https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html
#
# ### Структура данных для обучения имела вид: 
# author: str | text: str
#
# ### В качестве метрик качества была выбрана метрика Mean Accuracy
# https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html#sklearn.naive_bayes.MultinomialNB.score

# +
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np

import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('stopwords')

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# +
# merge all files from ./data
mypath: str = './data/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f != '.gitkeep']
li = []

for filename in onlyfiles:
    df = pd.read_csv(mypath+filename, sep=',', names=['text', 'position'])
    li.append(df)
# -

# read data
df = pd.concat(li, axis=0, ignore_index=True)
df.dropna(inplace=True)


# Defining a module for Text Processing
def text_process(tex):
    nopunct = [char for char in tex if char not in string.punctuation]
    nopunct = ''.join(nopunct)
    a = ''
    i = 0
    for i in range(len(nopunct.split())):
        b = lemmatiser.lemmatize(nopunct.split()[i], pos="v")
        a = a + b + ' '
    return [word for word in a.split() if word.lower() not in stopwords.words('russian') or word.lower() not in stopwords.words('english')]


# prepare data
lemmatiser = WordNetLemmatizer()
y = df['position']
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(y)
X = df['text']
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state=1234)

# +
# defining the bag-of-words transformer on the text-processed corpus
bow_transformer = CountVectorizer(analyzer=text_process).fit(X_train)

# transforming into Bag-of-Words and hence textual data to numeric
text_bow_train = bow_transformer.transform(X_train)

# transforming into Bag-of-Words and hence textual data to numeric
text_bow_test = bow_transformer.transform(X_test)
# -

# train model
model = MultinomialNB()
model = model.fit(text_bow_train, y_train)

# get mean accuracy of model
print('Точность модели на обучающей выборке = {}%'.format(round(model.score(text_bow_train, y_train), 3)))
print('Точность модели на валидационной выборке = {}%'.format(round(model.score(text_bow_test, y_test), 3)))

# check the position of possible author 
text = input('Введите текст для проверки работы модели')
to_predict = np.array(text).reshape(1,)
text_bow_val = bow_transformer.transform(to_predict)
print(labelencoder.inverse_transform(model.predict(text_bow_val)))


