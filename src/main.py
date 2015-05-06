# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:07:11 2015
Data Science Final Project 
@author: j_ast_000
"""

import os
import loadData as ld

def main():
    print "Welcome to my data science project" 
    pickleFileName = 'billData.pickle'
    if os.path.isfile(pickleFileName):
        ld.loadData(pickleFileName)
        

if __name__ == "__main__":
    main()
