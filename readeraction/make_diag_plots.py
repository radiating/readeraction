#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 21:58:27 2017

@author: tingzhu
"""

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, time, glob
import seaborn as sb

# function makes 3 plots to show cummulative number of comments, thumb-ups
# and replies over time (in hours)
def plot_comments_vs_time(comment_df):
    date_time=comment_df['time']
    epoch=[]
    for t in date_time:
        pattern='%Y-%m-%d %H:%M:%S'
        epoch.append(int(time.mktime(time.strptime(t, pattern))))
    
    epoch=(np.array(epoch)-min(epoch))/60/60

    #### ------ subplot 1
    plt.figure()
    plt.subplot(1,3,1)
    plt.hist(epoch,cumulative=True,histtype='step',linestyle='solid',color='black')
    plt.xlabel('Time (hour)')
    plt.ylabel('Cummulative number of comments')
    
    #### ------ subplot 2
    recommendation_col=comment_df['recommendation']
    plt.subplot(1,3,2)
    plt.scatter(epoch,recommendation_col,s=8,marker='o',label='# of thumb-up')
    plt.ylabel('# of thumb-ups for each comment')
    plt.xlabel('Time (hour)')

    nytpick_col=recommendation_col[comment_df['nyt_pick']==True]
    if len(nytpick_col)>0:
        nytpick_epoch=epoch[comment_df['nyt_pick']==True]
        plt.scatter(nytpick_epoch,nytpick_col,s=12,marker='*',c='b',label='NYT pick')
        plt.legend(frameon=True)

    #### ------ subplot 3
    reply_col=comment_df['replies']
    ax=plt.subplot(1,3,3)
    plt.scatter(epoch,reply_col,marker='o',s=8,label='# of reply')    
    plt.ylabel('# of replies for each comment')
    plt.xlabel('Time (hour)')
    nytpick_col=reply_col[comment_df['nyt_pick']==True]
    if len(nytpick_col)>0:
        nytpick_epoch=epoch[comment_df['nyt_pick']==True]
        plt.scatter(nytpick_epoch,nytpick_col,s=12,marker='*',c='b',label='NYT pick')
        plt.legend(frameon=True)
        #ax.legend(loc='upper center',frameon=True)
    
    plt.tight_layout()

##########
    plt.tight_layout()

    fig_name_only=str(time.time())+'.png'        
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    plt.savefig(plotfile,dpi=500)
    plotfile=os.path.join('static/',fig_name_only)
    return plotfile
  
# function makes two plots:
# 1) number of recommendations each comment received + labeling comment if selected by NYTimes
# 2) number of replies each comment received 
# Two plots are combined into a single figure for web app
def plot_comments_by_picks(comment_df):
    date_time=comment_df['time']
    recommendation_col=comment_df['recommendation']
    reply_col=comment_df['replies']
  
    epoch=[]
    for t in date_time:
        pattern='%Y-%m-%d %H:%M:%S'
        epoch.append(int(time.mktime(time.strptime(t, pattern))))

    epoch=(np.array(epoch)-min(epoch))/60/60
    plt.figure()
    plt.subplot(121)
    
    plt.plot(epoch,recommendation_col,'*',label='Recommendation')
    plt.ylabel('Number of recommendations for each comment')
    plt.xlabel('Time since first comment (hour)')
    
    
    nytpick_col=recommendation_col[comment_df['nyt_pick']==True]
    if len(nytpick_col)>0:
        nytpick_epoch=epoch[comment_df['nyt_pick']==True]
        plt.plot(nytpick_epoch,nytpick_col,'o',color='r',label='NYT pick')
        plt.legend()
     
    plt.subplot(122)
    plt.plot(epoch,reply_col,'*')    
    plt.ylabel('Number of replies for each comment')
    plt.xlabel('Time since first comment (hour)')

    fig_name_only=str(time.time())+'-nytpick.png'        
 
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    plt.savefig(plotfile)
    plotfile=os.path.join('static/',fig_name_only)
    
    return plotfile

# function makes 3 plots:
# 1) distribution of similarity index for all comments
# 2) similarity index vs. length of comments
# 3) similarity index vs. num of thumb-ups/comment
# 3 plots are combined into a single figure for web app
def plot_comments_by_readeraction(comment_df):
    date_time=comment_df['time']
    
    similarity_col=comment_df['similarity']
    recommendations_col=comment_df['recommendation']
    segments=[0,0.25,0.5,0.75,0.9,1]
    legend_names=['0-0.25','0.25-0.5','0.5-0.75','0.75-0.9','0.9-1']
    
    epoch=[]
    for t in date_time:
        pattern='%Y-%m-%d %H:%M:%S'
        epoch.append(int(time.mktime(time.strptime(t, pattern))))

    epoch=(np.array(epoch)-min(epoch))/60/60
########
    plt.figure()
    plt.subplot(131)
    plt.hist(similarity_col,bins=20)
    plt.xlabel('Similarity index')
    plt.ylabel('Count of comments')
    
    plt.subplot(132)
    plt.scatter(comment_df['similarity'],comment_df['length'],s=8)
    plt.xlabel('Similarity index')
    plt.ylabel('Length of each comment')

    plt.subplot(133)
    plt.scatter(comment_df['similarity'],comment_df['recommendation'],s=8)
    plt.xlabel('Similarity index')
    plt.ylabel('# of thumb-ups for each comment')
    
    plt.tight_layout()
    
    fig_name_only=str(time.time())+'-nytpick.png'        
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    plt.savefig(plotfile,dpi=500)
    plotfile=os.path.join('static/',fig_name_only)
 
    return plotfile

# function plots the distribution of topics for a given article
def plot_topics_for_article(topics_guide_df,new_doc_lda_result):
    # topics_guide is a dataframe (num_topics x 2 cols) with headers [topic id, top words]
    # new_doc_lda_result is a list of tuples (topic id, percent)
    
    topic_ind=[topic[0] for topic in new_doc_lda_result]
    percent=[topic[1] for topic in new_doc_lda_result]
    
    sb.set_palette(sb.color_palette("husl",len(topic_ind)))
    print('Preparing to plot topics breakdown for new document')
   
    fig = plt.figure()
    ax = plt.subplot(111)
   
    for i in np.arange(len(topic_ind)): 
       ax.bar(i,percent[i],label=' '.join([''.join(['T',str(topic_ind[i]+1)]),str(topics_guide_df['Top words'][topic_ind[i]])]))
   
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),ncol=1, fancybox=True, shadow=True,fontsize=14)
    ax.set_xlabel('LDA topics',fontsize=18)
    ax.set_ylabel('Probability',fontsize=18)
   
    labels=tuple(["T"+str(i+1) for i in topic_ind])
   
    plt.xticks(np.arange(len(topic_ind)), labels,fontsize=18)
    plt.yticks(fontsize=18)
 
    fig_name_only=str(time.time())+'-newdoc_topics.png'        
    plotfile=os.path.join('/home/ubuntu/InsightProject/readeraction/readeraction/static',fig_name_only)
    fig.savefig(plotfile,bbox_inches='tight')
    plotfile=os.path.join('static/',fig_name_only)

    return plotfile
