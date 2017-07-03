#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 19:26:47 2017

@author: tingzhu
"""

from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.models.phrases import Phrases,Phraser
from nltk.corpus import stopwords
from gensim.corpora import Dictionary

# function cleans (a list of) articles' texts
# article_list is a 'list'
def clean_articles(article_list):

    stop0 = set(stopwords.words('nyt0'))
    stop1 = set(stopwords.words('nyt1'))
    stop2 = set(stopwords.words('nyt2'))

    tokenizer=RegexpTokenizer(r'\w+')
    clean_article_list=[]
    for orig_text in article_list:
       orig_text=" ".join(orig_text.lower().split("’"))
       orig_text= [i for i in orig_text.split() if i not in stop0]
       orig_text=" ".join([i for i in orig_text if i not in stop1])
       orig_text=tokenizer.tokenize(orig_text)
       clean_article_list.append([i for i in orig_text if i not in stop2])
       
    clean_article_list=[[token for token in article if not token.isnumeric()] for article in clean_article_list]
    
    # prepares to make tri-grams of words 
    phrases= Phrases(clean_article_list, min_count=6)
    trigram = Phraser(phrases)
    trigram_list=[]
    for sent in clean_article_list:
        trigram_list.append(trigram[sent])
    
    # catch any bi-grams left over 
    phrases= Phrases(trigram_list, min_count=5)
    bigram = Phraser(phrases)
   
    final_list=[]
    for sent in trigram_list:
        final_list.append(bigram[sent])
    
    clean_trigram_article_list=final_list
     
    clean_article_list=[[token for token in article if len(token) >1] for article in clean_trigram_article_list]
    lemmatizer = WordNetLemmatizer()
    final_article_list = [[lemmatizer.lemmatize(token) for token in article] for article in clean_article_list]

    
    return final_article_list
