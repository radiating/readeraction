#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 16:41:31 2017

@author: tingzhu
"""


import requests
import time
from bs4 import BeautifulSoup
import readeraction.config_readeraction as config

# function that connects to NYTimes API and downloads URL of articles
# which are labeled the 'topic' (ie. news topic)
def get_articles(topics,date):
    
    print("Retriving articles in topics:",topics)    
    print(".........")
    nyt_key=config.nyt_key_article
    nyt_api = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'
    query_term='fq=news_desk:("'+topics+'") AND document_type:("article")'
    
    api_key='api-key='+nyt_key
    sort='sort=newest'
   
    all_articles=[]
    packet=0 # every packet has 10 articles
    offset_counter=0
    next_page=True
    
    while next_page and len(all_articles)<3000:
               
        print("Load in packet = ", packet)
        end_date='end_date='+date
        
        page="page="+str(packet)
        offset="offset="+str(offset_counter)
        json_url='&'.join([nyt_api,query_term,page,offset,sort,end_date,api_key])
        try:
            json_tbl=requests.get(json_url).json()
        except:
            print("Too much json request at NYT comment API. Sleep 4 sec")
            time.sleep(4)
            try:
                json_tbl=requests.get(json_url).json()
            except:
                print("STILL too much json request at NYT comment API. Sleep 4 sec")
                break
            
        num_articles_inPacket=len(json_tbl['response']['docs'])
        print('retrieve ',num_articles_inPacket,' articles')

        if num_articles_inPacket > 0:
            print()
            docs_perpage=json_tbl['response']['docs']
            all_articles=all_articles+docs_perpage
            time.sleep(1.5)
        
            packet=packet+1
        
            if packet == 120:
                date=docs_perpage[9]['pub_date'][:10].replace('-','') 
                packet=1
        else:
            next_page=False             
            print('last json_url: ', json_url)
            print('--------- Stop at article no. ', len(all_articles), '-----------')

    return all_articles

# function returns the body of the article text
# which is scraped from the article online directly
def get_articleBody(doc):
    each_article=[]
    failed_article=[]
    article_url=doc['web_url']    
    if 'http' in article_url:
        try:
            webpage = requests.get(article_url)
            soup = BeautifulSoup(webpage.text,"html.parser")
            PRG = soup.find_all("p",{"class":"story-body-text story-content"})
            if PRG:
                each_article=combine_paragraphs(PRG)
            else:
                PRG = soup.find_all("p",{"itemprop":"articleBody"}) 
                if PRG:
                    each_article=combine_paragraphs(PRG)    
                else:
                    print('bad html, no soup')
                    failed_article=article_url
        except:
            print('bad url (request): ',article_url)
    else:
        print('bad url (without http): ',article_url)
                
    return each_article, failed_article
    
# function combines paragraphs of an article into one complete body of text  
def combine_paragraphs(soup_obj):
    article_complete=[]
    for p in soup_obj:
        article_complete.append(p.get_text())
        
    article_complete=' '.join(article_complete)
    print(len(article_complete.split()))
    return article_complete

# function gets the text body of an article given its url
def get_article_by_url(article_url):
    article_body=[]
    failed_url=[]       
    if 'http' in article_url:
        try:
            webpage = requests.get(article_url)
            soup = BeautifulSoup(webpage.text,"html.parser")
            PRG = soup.find_all("p",{"class":"story-body-text story-content"})
            if PRG:
                article_body=combine_paragraphs(PRG)
            else:
                PRG = soup.find_all("p",{"itemprop":"articleBody"}) 
                if PRG:
                    article_body=combine_paragraphs(PRG)    
                else:
                    print('bad html, no soup')
                    failed_url=article_url
        except:
            print('bad url (request): ',article_url)
    else:
        print('bad url (without http): ',article_url)
                
    return article_body,failed_url

# function gets the basic info (article headline in current version) from 
# an article given its url
def get_article_meta(article_url):
    print("Retriving single article for meta info......")    
    
    nyt_key=config.nyt_key_article
    nyt_api = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'
    query_term='fq=web_url:("'+article_url+'")'
    api_key='api-key='+nyt_key
    fl_term='fl=headline'
    json_url='&'.join([nyt_api,query_term,fl_term,api_key])
    
    try:
        json_tbl=requests.get(json_url).json()
    except:
        print("Too much json request at NYT comment API. Sleep 4 sec")
        time.sleep(4)
        try:
            json_tbl=requests.get(json_url).json()
        except:
            print("STILL too much json request at NYT comment API. Sleep 4 sec")
            headline='unable to retrieve headline. try again later...'
            
    headline=json_tbl['response']['docs'][0]['headline']['main']
    
    return headline
