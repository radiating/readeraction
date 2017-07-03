#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:13:15 2017

@author: tingzhu
"""

#### to check which connection is ON:
##   lsof -i:5000

from readeraction import app
app.run(debug = True)
