# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:07:11 2015
Data Science Final Project 
@author: j_ast_000
"""

import os
import loadData as ld
import pickle

REBUILD_DATA = False;

def main():
    print "Welcome to my data science project" 
    pickleFileName = 'billData.pickle'
    if REBUILD_DATA:
        os.remove(pickleFileName)
        
    if os.path.isfile(pickleFileName):
        pickle.load(pickleFileName)
        print 'loaded previously saved data'
    else:
        ld.loadData(pickleFileName)
        

if __name__ == "__main__":
    main()
