#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 18:27:45 2017

@author: tingzhu
"""

import pandas as pd
import numpy as np
import time
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import readeraction.clf_trainer as clf_trainer
import readeraction.config_readeraction as config

# function converts a table(list) of comments into a sql database
# also append the list of similarity value for each comment
def commentlist_to_sql(comments_list,dbname,similarity_list):
    columns=['time','user_display_name','user_location','comments','recommendation','replies','toxicity','nyt_pick','similarity']
    df=pd.DataFrame(columns=columns,index=np.arange(len(comments_list)))
    
    for i in np.arange(len(comments_list)):
        df.loc[i]['time']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comments_list[i]['createDate'])))
        df.loc[i]['user_display_name']=comments_list[i]['userDisplayName']
        df.loc[i]['user_location']=comments_list[i]['userLocation']
        df.loc[i]['comments']=comments_list[i]['commentBody']
        df.loc[i]['recommendation']=comments_list[i]['recommendations']
        df.loc[i]['replies']=comments_list[i]['replyCount']
        df.loc[i]['nyt_pick']=comments_list[i]['editorsSelection']
        df.loc[i]['similarity']=similarity_list[i]

    # load in the "inappropriate comment" classifier
    full_path='/home/ubuntu/InsightProject/readeraction/readeraction/'
    clf_picklefilename=full_path+'toxicity_clf.pkl'
 
    # classify comments whether they are apropriate or not
    toxicity_clf=clf_trainer.retrieve_toxicity_clf(clf_picklefilename)
    df_toxic_clf=clf_trainer.apply_toxicity_clf(toxicity_clf, df)
  
    username='postgres'
    engine = create_engine('postgres://%s:%s@localhost/%s'%(username,config.postgres_pw,dbname))
    conn = engine.connect()
    df.to_sql(dbname, engine, if_exists='replace')

    return df
        
        
        
        
