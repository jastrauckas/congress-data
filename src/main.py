# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:07:11 2015
Data Science Final Project 
@author: j_ast_000
"""

import os
import loadData as ld
import pickle
import numpy as np
import sklearn
from sklearn import cross_validation, tree

REBUILD_DATA = False;

def crossValidate(X, y):
    	n = X.shape[0]
	kf = cross_validation.KFold(n, n_folds=20)

	clf = tree.DecisionTreeClassifier()
	X = sklearn.preprocessing.normalize(X)
	accuracies = []
	for train_index, test_index in kf:
		X_train, X_test = X[train_index], X[test_index]
		y_train, y_test = y[train_index], y[test_index]

		clf.fit(X_train,y_train)
		accuracies.append( clf.score(X_test,y_test) )
	ave_accuracy = sum(accuracies)/len(accuracies)
	print "%f performance accuracy" % ave_accuracy
 
def getPassedPercent(y):
     passedPct = float(np.count_nonzero(y)) / len(y)
     print str(passedPct) + '% of bills passed'
     return passedPct

def main():
    print "Welcome to my data science project" 
    pickleFileName = 'billData.pickle'
    if REBUILD_DATA or not os.path.isfile(pickleFileName):
        print 'Loading data from json files'
        ld.loadData(pickleFileName)
        
    else:
        print 'Loading previously saved data'
    
    pickleFile = open(pickleFileName, 'rb')
    dataSet = pickle.load(pickleFile)
    X = dataSet.data
    y = dataSet.labels
    print 'Got data with: ' + str(len(X[:,0])) + ' observations'
    getPassedPercent(y)
    crossValidate(X,y)

if __name__ == "__main__":
    main()
