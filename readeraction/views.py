#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:35:21 2017

@author: tingzhu
"""
import readeraction.config_readeraction as config
from flask import render_template,redirect
from readeraction import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request
from readeraction.convert2sql import commentlist_to_sql
from readeraction.get_comments import make_comment_tbl,load_sampleComments
from readeraction.get_articles import get_article_meta
from readeraction.make_diag_plots import plot_comments_by_readeraction,plot_comments_vs_time,plot_comments_by_picks,plot_topics_for_article
from readeraction.analyze_similarity import get_lda_results_for_newdoc, add_comment_similarity_and_plots
from readeraction.build_lda import interpret_main_lda
import string


@app.route('/')
@app.route('/index')
def index():
    return redirect("http://readeraction.press/demo")

@app.route('/author')
def about_me():
     return redirect("https://linkedin.com/in/zhuting")
     
@app.route('/blog')
def goto_blog():
   return render_template("blog.html")

@app.route('/demo')
def input():
    return render_template("demo.html")

@app.route('/output',methods=['GET','POST'])
def output():    
   
    topic_option = request.args.get('news_topic')
    if topic_option: # if user selects pre_downloaded API data
        print('Preloaded topic:', topic_option)     
        comments_df,web_url=load_sampleComments(topic_option)
        topic_option=topic_option.lower()
        remove_digits = str.maketrans('', '', string.digits)
        topic_option = topic_option.translate(remove_digits)

    else: # if user enters a URL
        web_url = request.args.get('web_url')
        topic_option=request.args.get('topic_option')
        topic_option=topic_option.lower()
        print('User entered topic:', topic_option)
        comments_df=make_comment_tbl(web_url)
    
    headline = get_article_meta(web_url)    
    user = 'postgres'          
    host = 'localhost'   
    dbname = 'comment_tbl'

    ldamodel,dictionary,new_doc_lda_result=get_lda_results_for_newdoc(web_url,topic_option)
    if topic_option == 'politics':
       num_topics=config.politics_topics['num_topics']
    elif topic_option == 'business':
       num_topics=config.business_topics['num_topics']
    elif topic_option =='sports':
       num_topics=config.sports_topics['num_topics']
    else:
       num_topics=config.num_topics
    print('LDA model with ',num_topics,' of topics')    
    topics_guide_df=interpret_main_lda(ldamodel,dictionary,num_topics)
    newdoc_topics_plot=plot_topics_for_article(topics_guide_df,new_doc_lda_result)
    
    print('Calculate similarity for comments')
    similarity_list,largeDiff_plot_name,smallDiff_plot_name=add_comment_similarity_and_plots(ldamodel,dictionary,comments_df,new_doc_lda_result,num_topics)
    print(largeDiff_plot_name)
    print(smallDiff_plot_name)

    if not similarity_list:
        similarity_list=0*len(comments_df)
        print('Fail to compute similarity')
    shorter_df=commentlist_to_sql(comments_df,dbname,similarity_list)

    
    time_plot = plot_comments_vs_time(shorter_df)
    nytpick_plot=plot_comments_by_picks(shorter_df)
    readeractionpick_plot=plot_comments_by_readeraction(shorter_df)
 
    url='postgres://%s:%s@%s/%s'%(user,config.postgres_pw,host,dbname)
    engine=create_engine(url)
    con=engine.connect()

    query = "SELECT * FROM comment_tbl WHERE toxicity='Yes'"
    print(query)
    query_results=pd.read_sql_query(query,con)
    print(query_results)
    bad_comments = []
    for i in range(0,query_results.shape[0]):
        bad_comments.append(dict(user_displayname=query_results.iloc[i]['user_display_name'], user_location=query_results.iloc[i]['user_location'], commentBody=query_results.iloc[i]['comments']))
     
    query = "SELECT * FROM comment_tbl WHERE nyt_pick = 'True' ORDER BY similarity DESC"
    print(query)
    query_results=pd.read_sql_query(query,con)
    print(query_results)
    nytpick_comments = []
    for i in range(0,query_results.shape[0]):
        nytpick_comments.append(dict(commentBody=query_results.iloc[i]['comments'],recommendation=query_results.iloc[i]['recommendation'],similarity=query_results.iloc[i]['similarity']))
    
    query = "SELECT * FROM comment_tbl WHERE toxicity='No' ORDER BY similarity DESC LIMIT 4"
    print(query)
    query_results=pd.read_sql_query(query,con)
    print(query_results)
    top_sim_comments = []
    for i in range(0,query_results.shape[0]):
        top_sim_comments.append(dict(index=query_results.iloc[i]['index'], post_time=query_results.iloc[i]['time'],commentBody=query_results.iloc[i]['comments'],recommendation=query_results.iloc[i]['recommendation'],nyt_pick=query_results.iloc[i]['nyt_pick'],similarity=query_results.iloc[i]['similarity']))
    
    query = "SELECT * FROM comment_tbl WHERE toxicity='No' ORDER BY similarity ASC LIMIT 4"
    print(query)
    query_results=pd.read_sql_query(query,con)
    print(query_results)
    low_sim_comments = []
    for i in range(0,query_results.shape[0]):
        low_sim_comments.append(dict(index=query_results.iloc[i]['index'], post_time=query_results.iloc[i]['time'],commentBody=query_results.iloc[i]['comments'],recommendation=query_results.iloc[i]['recommendation'],nyt_pick=query_results.iloc[i]['nyt_pick'],similarity=query_results.iloc[i]['similarity']))
    
    return render_template("output.html", headline=headline,top_sim_comments=top_sim_comments,low_sim_comments=low_sim_comments, nytpick_comments=nytpick_comments,bad_comments = bad_comments, time_plot = time_plot,topic_option=topic_option,nytpick_plot=nytpick_plot,readeractionpick_plot=readeractionpick_plot,newdoc_topics_plot=newdoc_topics_plot,lowSim_plot_name=largeDiff_plot_name,highSim_plot_name=smallDiff_plot_name)
