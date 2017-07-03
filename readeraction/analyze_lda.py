#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:13:42 2017

@author: tingzhu
"""

import numpy as np
import pandas as pd
import readeraction.clean_text as clean_text
import readeraction.get_articles as get_articles
from gensim.corpora import Dictionary
import random
import seaborn as sb
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os, time, glob, math


# function applies LDA model to compute LDA topics of new article
def compareToNewdoc(ldamodel, lda_dictionary, new_doc_url):
    new_doc=get_articles.get_article_by_url(new_doc_url)
    if isinstance(new_doc,tuple):
        new_doc=new_doc[0]
    
    new_doc_clean=clean_text.clean_articles([new_doc])

    new_doc_corpus = lda_dictionary.doc2bow(new_doc_clean[0])
    new_doc_lda=ldamodel[new_doc_corpus]
    
    if len(new_doc_clean) == 1 and len(new_doc_clean[0]) >1:
        new_doc_clean=new_doc_clean[0]
        
    if check_corpus(lda_dictionary,new_doc_clean,new_doc_corpus) != 0:
        print('ERROR in corpus application from lda model to new document')
        exit(1)
    
    print('Break down of topics for new document:')
    print('(topic_id, percentage)')
    print('topic top words\n')
    for topic in new_doc_lda:
        print(topic)
        s=ldamodel.print_topic(topic[0],topn=5)
        print(s)
        print('')
        
    return new_doc_lda

# function checks whether the new document has a corpus in conflict with LDA model
def check_corpus(lda_dictionary,new_doc,new_corpus):
    fail_times=0
    r3=random.sample(set(np.arange(len(new_corpus))),min(3,len(new_corpus)))
    for r in r3:
        expected_locations=[i for i, word in enumerate(new_doc) if word ==lda_dictionary[new_corpus[r][0]]]
        times_by_corpus=new_corpus[r][1]
        if len(expected_locations) != times_by_corpus:        
            print('For random-chosen word:', lda_dictionary[new_corpus[r][0]], ' with word_id',r)
            print('Expected in sentence location: ',[i for i, word in enumerate(new_doc[0]) if word ==lda_dictionary[new_corpus[r][0]]])
            print('According to corpus, it appears ',new_corpus[r][1],'times')
            fail_times=fail_times+1

    return fail_times
 
# function applies LDA model to compute LDA topics of each comment
def compareToComments(ldamodel, lda_dictionary,comments_tbl):
  
    new_comment=[comment_body['commentBody'] for comment_body in comments_tbl]
    new_comment_clean=clean_text.clean_articles(new_comment)
    print('Cleaned ',len(new_comment), ' raw comments for lda topic extration.')

    if len(new_comment_clean)>1: 
        print_topics=0
    else:
        print_topics=1
    
    comment_topic_result=[]
    comment_corpus_result=[]
    c=0
    for comment in new_comment_clean:
        new_comment_corpus = lda_dictionary.doc2bow(comment)
        if check_corpus(lda_dictionary,comment,new_comment_corpus) == 0:
            new_comment_lda=ldamodel[new_comment_corpus]
            comment_corpus_result.append(new_comment_corpus)
            if print_topics==1:
                print('Break down of topics for new document:')
                print('(topic_id, percentage)')
                print('topic top words\n')
                for topic in new_comment_lda:
                    print(topic)
                    s=ldamodel.print_topic(topic[0],topn=5)
                    print(s)
                    print('')
            comment_topic_result.append(new_comment_lda)    
        else:
            print('ERROR in corpus application from lda model to new document')
            print('Check returned results where tuples are (0,0)')
            comment_topic_result.append((0,0))
        c=c+1
    print('Finish comparing to comments')    
    return comment_topic_result,new_comment_clean

# function calculates cosine angle for all comments
def calc_cosine_list(article_vec,comments_list_vec, num_topics):
    list_cosine=[]
    for each_comment_vec in comments_list_vec:
        list_cosine.append(calc_cosine(each_comment_vec,article_vec,num_topics))
    
    high_angle_degree=80
    low_angle_degree=20
    
    large_diff=[i for i,x in enumerate(list_cosine) if x < math.cos(math.radians(high_angle_degree))]
    small_diff=[i for i,x in enumerate(list_cosine) if x > math.cos(math.radians(low_angle_degree))]
    
    print(len(large_diff),' comments with Cosine angle > ', high_angle_degree,' degree (', math.cos(math.radians(high_angle_degree)),')')
    print(len(small_diff),' comments with Cosine angle < ', low_angle_degree,' degree (', math.cos(math.radians(low_angle_degree)),')')
    
    return list_cosine, large_diff, small_diff
    
# function calculates cosine angle for each comment
def calc_cosine(vec1,vec2,num_topics):
    vec1_full=build_full_vec(vec1,num_topics)
    vec2_full=build_full_vec(vec2,num_topics)
    
    numerator = np.dot(vec1_full,vec2_full)
    denominator = np.sqrt(np.dot(vec1_full,vec1_full))*np.sqrt(np.dot(vec2_full,vec2_full))
    cosine_val=numerator/denominator
    
    return cosine_val

# function turns non-zero tuple of (topic, probability) into full LDA topic vector    
def build_full_vec(vec_of_tuples,num_topics):
    
    full_vec=np.zeros(num_topics)
    for tuple_pair in vec_of_tuples:
        full_vec[tuple_pair[0]]=tuple_pair[1]
        
    return full_vec


# function makes 4 plots of LDA topic distribution of a comment vs. an article
def plot_topic_distribution_multiple(new_doc_lda, comment_lda_all, list_cosine,num_topics):

    new_doc_full_vec=build_full_vec(new_doc_lda,num_topics)
    
    sort_index = np.argsort(list_cosine)
    
    # plot cases that are very different from new_doc
    # this requires the cosine to be small
    
    # sort_index from small to big (ascending)
    num_plots=4 
    fig = plt.figure()
    for i,v in enumerate(range(num_plots)):
    
        comment_num=sort_index[i] 
        comment_full_vec=build_full_vec(comment_lda_all[int(comment_num)],num_topics)
        v=v+1
        ax = plt.subplot(num_plots,1,v)
        topic_axis=np.arange(num_topics)*5
        width=0.8
        
        rects1=ax.bar(topic_axis,new_doc_full_vec,width,color=sb.xkcd_rgb['amber'])
        rects2=ax.bar(topic_axis+width,comment_full_vec,width,color='b')
    
        ax.set_ylabel('Probability')
        ax.set_xticks(topic_axis+width/2)
        ax.legend((rects1[0],rects2[0]),('article','comment #'+str(comment_num)),loc='lower left',bbox_to_anchor=(0,1),ncol=2,fontsize=10)
        ax.set_xticklabels(tuple([str(t+1) for t in range(num_topics)]),fontsize=8) 

    plt.subplots_adjust(hspace=1)
    fig_name_only='similarity_largeDiff_'+str(time.time())+'.png'        
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    fig.savefig(plotfile,dpi=600)
    plotfile_largeDiff=os.path.join('static/',fig_name_only)
     
    # choose from the last elements of sort_index from big to small (descending)
    num_plots=4 
    fig = plt.figure()
    for i,v in enumerate(range(num_plots)):
   
        comment_num=sort_index[len(sort_index)-i-1]
        comment_full_vec=build_full_vec(comment_lda_all[int(comment_num)],num_topics)
        v=v+1
        ax = plt.subplot(num_plots,1,v)
        topic_axis=np.arange(num_topics)*5
        width=0.8
        
        rects1=ax.bar(topic_axis,new_doc_full_vec,width,color=sb.xkcd_rgb['amber'])
        rects2=ax.bar(topic_axis+width,comment_full_vec,width,color='b')
    
        ax.set_ylabel('Probability')
        ax.set_xticks(topic_axis+width/2)
        ax.legend((rects1[0],rects2[0]),('article','comment #'+str(comment_num)),loc='lower left',bbox_to_anchor=(0,1),ncol=2,fontsize=10)
   
        ax.set_xticklabels(tuple([str(t+1) for t in range(num_topics)]),fontsize=8)
    
    plt.subplots_adjust(hspace=1)
    fig_name_only='similarity_smallDiff_'+str(time.time())+'.png'        
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    fig.savefig(plotfile,dpi=600)
    plotfile_smallDiff=os.path.join('static/',fig_name_only)
    
    # return the 2 saved figure file names
    return plotfile_largeDiff, plotfile_smallDiff


