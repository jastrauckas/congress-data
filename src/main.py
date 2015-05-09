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
from sklearn import cross_validation, tree, svm, lda
import matplotlib.pyplot as plt

REBUILD_DATA = False

def crossValidate(X, y):
    n = X.shape[0]
    y = np.ravel(y)
    kf = cross_validation.KFold(n, n_folds=100)

    clf = tree.DecisionTreeClassifier()
    #clf = svm.SVC()
    #clf = lda.LDA()
     
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
     
def plot_confusion_matrix(cm, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(iris.target_names))
    plt.xticks(tick_marks, iris.target_names, rotation=45)
    plt.yticks(tick_marks, iris.target_names)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
def getFeatureDistributions(X, labelNames):
    for l in range(len(labelNames)):
        label = labelNames[l]
        data = X[:,l]
        np.histogram(data)
        plt.figure()
        plt.hist(data)
        plt.title(label)
        plt.xlabel("Value")
        plt.ylabel("Frequency")  
        plt.show()

def getCategoryMap(bills):
    catMap = {}
    for bill in bills.values():
        category = bill.category
        if category in catMap:
            continue
        nextCatNum = len(catMap) + 1
        catMap[category] = nextCatNum
    print len(catMap)
    return catMap
    
def getFeatures(bills):
    numFeats = 4
    numRows = len(bills)
    catMap = getCategoryMap(bills)
    X = np.zeros((numRows, numFeats), dtype=float)  
    y = np.zeros((numRows, 1), dtype=int)
    thisRow = 0
    for bill in bills.values():
        # assign features and labels  
        label = -1 # other
        if bill.succeeded():
            label = 1
        elif bill.failed():
            label = 0
        else:
            continue
        catNum = catMap[bill.category]

        # once you add in a categorical feature, definitely want 
        X[thisRow, :] = [bill.cosponsorCount, bill.pctDemCosponsors, bill.pctRepCosponsors, catNum]
        y[thisRow] = label
        thisRow += 1
    return(X,y)

def main():
    plt.close("all")
    print "Welcome to my data science project" 
    pickleFileName = 'billData.pickle'
    if REBUILD_DATA or not os.path.isfile(pickleFileName):
        print 'Loading data from json files'
        ld.loadData(pickleFileName)
        
    else:
        print 'Loading previously saved data'
    
    pickleFile = open(pickleFileName, 'rb')
    bills = pickle.load(pickleFile)
    (X,y) = getFeatures(bills)
    print 'Got data with: ' + str(len(X[:,0])) + ' observations'
    getPassedPercent(y)
    
    # try kfolds
    crossValidate(X,y)
    
    # look at feature distributions
    labels = ['Number of cosponsors', '% Democratic Cosponsors', '% Republican Cosponsors', 'Numerical Category']
    getFeatureDistributions(X, labels)
    
    # train, leaving out most recent congress (113), and get confusion matrix

if __name__ == "__main__":
    main()
