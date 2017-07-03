#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 23:18:10 2017

@author: tingzhu
"""
import requests
import pandas as pd
import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt    
import readeraction.config_readeraction as config
import pickle

# function downloads article comments from NYTimes API
def make_comment_tbl(article_url):
    print("Retriving comments from article\n")
    print(article_url)
    print(".........")
    nyt_key=config.nyt_key_comment
    nyt_api = 'http://api.nytimes.com/svc/community/v3/user-content/url.json?'
    query_term='url='+article_url
    order='sort=oldest'
    api_key='api-key='+nyt_key
    
    all_comments=[]
    elem=0
    next_page=True
    # limit the number of calls to 2500 (10k/25)
    # daily call limit is 5000
    while next_page and elem < 10000: 
        print("Load in page = ", elem)
        offset="offset="+str(elem)
        json_url='&'.join([nyt_api,query_term,offset,order,api_key])
        
        try:
            json_tbl=requests.get(json_url).json()
        except:
            print("Too much json request at NYT comment API. Sleep 4 sec")
            time.sleep(2)
            try:
                json_tbl=requests.get(json_url).json()
            except:
                print("STILL too much json request at NYT comment API. Sleep 4 sec")
                break
        
        num_comments_perpage=len(json_tbl['results']['comments'])
        print('retrieve ', num_comments_perpage)
        
        if num_comments_perpage >0:
            print()
            comments_perpage=json_tbl['results']['comments']
            all_comments=all_comments+comments_perpage
            time.sleep(0.2)
            elem=elem+25
        else:
            next_page=False            
            print('total comments found = ', json_tbl['results']['totalCommentsFound'])
            print('total editor selection found = ', json_tbl['results']['totalEditorsSelectionFound'])
            print('total parents comments found = ', json_tbl['results']['totalParentCommentsFound'])
            print('total recommendations found = ', json_tbl['results']['totalRecommendationsFound'])
            print('total reply comments found = ', json_tbl['results']['totalReplyCommentsFound'])
            print('--------- Stop at elem ', elem, '-----------')
            print('----------Check remining API call limit -------')
            print('curl --head https://api.nytimes.com/svc/books/v3/lists/overview.json?api-key=<...> | grep -i "X-RateLimit"')

    return all_comments

# function returns the already-downloaded pickle-object of article comments
# given the topic name from the dropdown menu on the web app
def load_sampleComments(topic):
    options={'sports': './readeraction/comments_sports_rawjson.p',
            'politics1': './readeraction/comments_politics1_rawjson.p',
            'politics2': './readeraction/comments_politics2_rawjson.p',
            'politics3': './readeraction/comments_politics3_rawjson.p',
            'politics4': './readeraction/comments_politics4_rawjson.p',
            'business1': './readeraction/comments_business1_rawjson.p',
            'business2': './readeraction/comments_business2_rawjson.p',
            'business3': './readeraction/comments_business3_rawjson.p',
            'business4': './readeraction/comments_business4_rawjson.p' 
            }
    
    links={'sports': 'https://www.nytimes.com/2017/05/05/sports/basketball/lonzo-lavar-ball-shoes-zo2.html',
            'politics1':'https://www.nytimes.com/2017/06/09/us/politics/trump-comey.html',
            'politics2':'https://www.nytimes.com/2017/06/08/us/politics/comey-hearing-trump-russia.html',
            'politics3':'https://www.nytimes.com/2017/06/01/climate/trump-paris-climate-agreement.html',
            'politics4':'https://www.nytimes.com/2017/06/27/us/politics/republicans-struggle-to-marshal-votes-for-health-care-bill.html',
            'business1': 'https://www.nytimes.com/2017/06/14/technology/one-way-to-fix-uber-think-twice-before-using-it.html',
            'business2': 'https://www.nytimes.com/2017/06/14/business/women-sexism-work-huffington-kamala-harris.html',
            'business3': 'https://www.nytimes.com/2017/06/06/technology/tech-billionaires-education-zuckerberg-facebook-hastings.html',
            'business4': 'https://www.nytimes.com/2017/06/23/business/dealbook/irs-private-collectors.html'
           }
    
    filename=options[topic]
    comment_tbl = pickle.load( open(filename, "rb" ) )
    web_url=links[topic]
    
    return comment_tbl,web_url

