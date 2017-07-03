#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 09:51:32 2017

@author: tingzhu
"""
from __future__ import division


import readeraction.get_articles as get_articles

import numpy as np
import gensim
import pandas as pd

from gensim.corpora import Dictionary
import readeraction.clean_text as clean_text
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# function builds LDA model based on many NYTimes articles
def build_lda_dict_corpus(body, train_num_topics):

    # if "body" arg is filename of file that's already in html texts
    if isinstance(body,str): 
        f = open(body, 'r')
        articles_list = f.readlines()
        num_articles=len(articles_list)
        print('number of articles: ', num_articles)
    else: # input arg is mongo database
        articles=body
        num_articles=articles.count() 
        print('number of articles: ', num_articles)
        
        all_articles=[]
        failed_articles=[]
        start_ind=0
        for i in np.arange(start_ind,num_articles):
            article_dict=articles[int(i)]
            # article texts need to be scraped 
            each_article, failed = get_articles.get_articleBody(article_dict)
            all_articles.append(each_article)
            failed_articles.append(failed)
        print('Finished downloading articles body text')    
        articles_list = [x for x in all_articles if x != []]
        failed_url = [x for x in failed_articles if x != []]

        outfile=open('failed_url.txt','w')
        for item in failed_url:
            outfile.write("%s\n" % item)    
            
    # raw article texts needs to be cleaned (remove stop words, lemmentizing
    # and create bi/tri-grams
    articles_list =clean_text.clean_articles(articles_list)
    print('Finished tokenizing and cleaning all articles')
    
    # create Dictionary object and turn words of all texts into a corpus
    dictionary = Dictionary(articles_list)
    dictionary.filter_extremes(no_below=20, no_above=0.5)
    corpus = [dictionary.doc2bow(article) for article in articles_list]
    
    # create LDA object
    lda_model = gensim.models.ldamodel.LdaModel
    
    # keep track of Average Jaccard score
    score_num_topics=[]
    if train_num_topics==0: #loop through different LDA topic numbers
        print('Determining number of topics in LDA model')
        for num_topics in np.arange(3,30,3):
            ldamodel = lda_model(corpus, num_topics=num_topics, alpha='auto', id2word = dictionary, passes=4)
            score_num_topics.append(calc_AF_byGreene(ldamodel,num_topics))
        plt.plot(np.arange(3,30,3),score_num_topics)  
    else: # generate LDA model using pre-defined LDA topic number
        num_topics=train_num_topics
        print('Building LDA model with ',num_topics,' topics')
        ldamodel = lda_model(corpus, num_topics=num_topics, alpha='auto', id2word = dictionary, passes=4)
        score_num_topics.append(calc_AF_byGreene(ldamodel,num_topics))
    
    print('Done LDA modelling')        
    print('=== get topics list:')        
    print('ldamodel.show_topics(num_topics=min(10,num_topics),num_words=10)')
    print('=== get individual topic distribution:')
    print('print(ldamodel.get_topic_terms(topic_id,10)')

    return dictionary, corpus, ldamodel, articles_list

# calculate average jaccard number for all topics of LDA model
def calc_AF_byGreene(ldamodel,num_topics):
    import itertools
    L=list(itertools.combinations(range(num_topics),2))
    AJ_pair_val=[]
    for pair in L:
        topic1=ldamodel.get_topic_terms(pair[0],10)
        topic2=ldamodel.get_topic_terms(pair[1],10)
        val=calc_AJpair_byGreene(topic1,topic2)
        AJ_pair_val.append(val)
    
    print(np.mean(AJ_pair_val))
    return np.mean(AJ_pair_val)

# calculate average jaccard number for two topics of LDA model
def calc_AJpair_byGreene(topic1, topic2):
    
    depth=10
    AJ=0
    for d in np.arange(depth):
        R1=[]
        R2=[]
        for t in np.arange(0,d+1):
            R1.append(topic1[t][0])
            R2.append(topic2[t][0])
        a=len(set(R1).intersection(R2))
        b=len(list(set().union(R1,R2)))

        if b==0 and a==0:
            gamma=0
        elif b==0 and a!=0:
            print('error in AJ calculation')
            
        else:
            gamma=a/b
        AJ=AJ+gamma
    AJ=AJ/depth    
    return AJ

# auxi-function saves LDA model and dictionary for later use
def save_lda_model(ldamodel_object, dictionary_object,object_names):
    ldamodel_object.save(object_names[0])
    dictionary_object.save(object_names[1])
    print("Saved ldamodel as '", object_names[0],"'")
    print("Saved dictionary as '", object_names[1],"'")

# auxi-function returns the saved LDA model and dictionary
def return_lda_model(object_names):
    print("Reload ldamodel from '", object_names[0],"'")
    print("Reload dictionary from '", object_names[1],"'")
    select_ldamodel = gensim.models.LdaModel.load(object_names[0])
    select_dictionary = gensim.corpora.Dictionary.load(object_names[1])
    
    return select_ldamodel, select_dictionary

# function returns a dataframe with topic ID and top 5 words as columns given an LDA model
# num_topics is the total number of topics the LDA model is built on
def interpret_main_lda(main_lda,main_dict,num_topics):
    
    depth=5
    columns=['Topic ID','Top words']
    
    topics_df=pd.DataFrame(columns=columns,index=np.arange(num_topics))
    
    for i in range(num_topics):
        topics_df.loc[i]['Topic ID']=i
        main_lda.get_topic_terms(i,depth)
        topwords_list=[]
        for d in range(depth):
            topwords_list.append(main_dict[main_lda.get_topic_terms(i,depth)[d][0]])
        topics_df.loc[i]['Top words']=topwords_list
    print('Return topics of the main LDA')     
    return topics_df
    
    
