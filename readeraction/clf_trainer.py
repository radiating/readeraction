#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 10:12:39 2017

@author: tingzhu
"""

import pandas as pd
import urllib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import pickle
import numpy as np


def download_file(url, fname):
    urllib.request.urlretrieve(url, fname)
   
# function that trains a classifier to filter inappropriate comments   
def train_toxicity_clf():

#    # download annotated comments and annotations
#    ANNOTATED_COMMENTS_URL = 'https://ndownloader.figshare.com/files/7038044' 
#    ANNOTATIONS_URL = 'https://ndownloader.figshare.com/files/7383751' 
#                    
#    download_file(ANNOTATED_COMMENTS_URL, 'attack_annotated_comments.tsv')
#    download_file(ANNOTATIONS_URL, 'attack_annotations.tsv')
#    
    comments = pd.read_csv('attack_annotated_comments.tsv', sep = '\t', index_col = 0)
    annotations = pd.read_csv('attack_annotations.tsv',  sep = '\t')

    labels = annotations.groupby('rev_id')['attack'].mean() > 0.5
    comments['attack'] = labels
    
    # remove newline and tab tokens
    comments['comment'] = comments['comment'].apply(lambda x: x.replace("NEWLINE_TOKEN", " "))
    comments['comment'] = comments['comment'].apply(lambda x: x.replace("TAB_TOKEN", " "))
    
    # fit a simple text classifier
    train_comments = comments.query("split=='train'")
    test_comments = comments.query("split=='test'")
    clf = Pipeline([
        ('vect', CountVectorizer(max_features = 10000, ngram_range = (1,2))),
        ('tfidf', TfidfTransformer(norm = 'l2')),
        ('clf', LogisticRegression()),
    ])
    clf = clf.fit(train_comments['comment'], train_comments['attack'])
    auc = roc_auc_score(test_comments['attack'], clf.predict_proba(test_comments['comment'])[:, 1])
    print('Classifier training completed')
    print('Test ROC AUC: %.3f' %auc)

    print('Test CLF on examples:')
    # correctly classify nice comment
    clf.predict(['Thanks for you contribution, you did a great job!'])
        
    # now you can save it to a file
    with open('toxicity_clf.pkl', 'wb') as f:
        pickle.dump(clf, f)
    
    return clf

# function that returns pre-trained classifier
def retrieve_toxicity_clf(clf_picklefilename):
    
    with open(clf_picklefilename, 'rb') as f:
        clf = pickle.load(f)
    return clf

# function that applies classifier to flag comments that are inappropriate
def apply_toxicity_clf(toxicity_clf, comment_df): 
    
    for i in np.arange(len(comment_df.index)):
        if toxicity_clf.predict([comment_df.loc[i]['comments']]): 
            comment_df.loc[i]['toxicity']='Yes'
        else:
            comment_df.loc[i]['toxicity']='No'
    
    return comment_df   
            
            
            
