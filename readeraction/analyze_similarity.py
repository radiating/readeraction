#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 13:09:40 2017

@author: tingzhu
"""
import readeraction.analyze_lda as analyze_lda
import readeraction.build_lda as build_lda
import readeraction.config_readeraction as config

# function selects the LDA model depnding on the given news topic
def get_lda_results_for_newdoc(new_doc_url,topic):
    print('Choose LDA model based on selected topic of ', topic)
    filedir='/home/ubuntu/InsightProject/readeraction/readeraction/'
    if topic=='politics':
       object_names=[filedir+'politics_lda_'+ str(config.politics_topics['num_topics'])+'_'+str(config.politics_topics['num_pass']), filedir+ 'politics_dictionary_' + str(config.politics_topics['num_topics'])+'_'+str(config.politics_topics['num_pass'])]
    elif topic=='business':
       object_names=[filedir+'business_lda_'+ str(config.business_topics['num_topics'])+'_'+str(config.business_topics['num_pass']), filedir+ 'business_dictionary_' + str(config.business_topics['num_topics'])+'_'+str(config.business_topics['num_pass'])]
    elif topic=='sports':
       object_names=[filedir+'sports_lda_'+ str(config.sports_topics['num_topics'])+'_'+str(config.sports_topics['num_pass']), filedir+ 'sports_dictionary_' + str(config.sports_topics['num_topics'])+'_'+str(config.sports_topics['num_pass'])]
  
   
    print(object_names[0])
    print(object_names[1])
    
    # call up the LDA model
    ldamodel,dictionary=build_lda.return_lda_model(object_names)
  
    # apply LDA model to the article
    new_doc_lda_result=analyze_lda.compareToNewdoc(ldamodel, dictionary, new_doc_url)
    print('Finish analyzing topics for new doc')    
    return ldamodel,dictionary,new_doc_lda_result

# function returns cosine similarity for all comments, and 2 distribution plots
def add_comment_similarity_and_plots(ldamodel,dictionary,comments_tbl,new_doc_lda_result,num_topics):
    
    (comments_lda_result,comments_clean)=analyze_lda.compareToComments(ldamodel,dictionary,comments_tbl)
    (list_cosine, large_diff,small_diff)=analyze_lda.calc_cosine_list(new_doc_lda_result,comments_lda_result,num_topics)
    print('Finish calculating cosine values between new doc and comments')
    largeDiff_plot_name,smallDiff_plot_name=analyze_lda.plot_topic_distribution_multiple(new_doc_lda_result, comments_lda_result,list_cosine,num_topics)

    return list_cosine, largeDiff_plot_name,smallDiff_plot_name

