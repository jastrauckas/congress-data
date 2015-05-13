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
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

REBUILD_DATA = False

def getClassifier():
    clf = tree.DecisionTreeClassifier()
    #clf = svm.SVC()
    #clf = lda.LDA()
    return clf
    
def crossValidate(X, y):
    n = X.shape[0]
    y = np.ravel(y)
    kf = cross_validation.KFold(n, n_folds=100)

    clf = getClassifier()
     
    X = sklearn.preprocessing.normalize(X)
    accuracies = []
    for train_index, test_index in kf:
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        clf.fit(X_train,y_train)
        accuracies.append( clf.score(X_test,y_test) )
    ave_accuracy = sum(accuracies)/len(accuracies)
    print "%f performance accuracy" % ave_accuracy

def trainAndTest(X,y,z):
    Xtrain = np.zeros(X.shape, dtype=float)
    Xtest = np.zeros(X.shape, dtype=float)
    ytrain = []
    ytest = []
    totalRows = len(z)
    testRows = 0 
    trainRows = 0
    for i in range(totalRows):
        congressNum = z[i]
        if congressNum < 112:
            Xtrain[trainRows, :] = X[i,:]
            ytrain.append(y[i])
            trainRows += 1
        else:
            Xtest[testRows, :] = X[i,:]
            ytest.append(y[i])
            testRows += 1
    
    Xtrain = Xtrain[0:trainRows, :]
    ytrain = ytrain[0:trainRows]
    Xtest = Xtest[0:testRows, :]
    ytest = ytest[0:testRows]
    
    clf = getClassifier()
    clf.fit(Xtrain, ytrain)
    ypred = clf.predict(Xtest)
    accuracy = clf.score(Xtest, ytest)
    cm = confusion_matrix(ytest, ypred)
    print cm
    print 'TEST ACCURACY: ' + str(accuracy)
    return cm
    
 
def getPassedPercent(y):
     passedPct = float(np.count_nonzero(y)) / len(y)
     print str(passedPct) + '% of bills passed'
     return passedPct
     
def plotConfusionMatrix(cm, targetNames, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(targetNames))
    plt.xticks(tick_marks, targetNames, rotation=45)
    plt.yticks(tick_marks, targetNames)
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
    numFeats = 6
    numRows = len(bills)
    catMap = getCategoryMap(bills)
    congressMap = ld.getPartiesByCongress()
    X = np.zeros((numRows, numFeats), dtype=float)  
    y = np.zeros((numRows, 1), dtype=int)
    z = np.zeros((numRows, 1), dtype=int)
    thisRow = 0
    for bill in bills.values():
        congressNum = int(bill.congress)
        congressData = congressMap[congressNum]
        hPctDem = congressData.housePctDem
        hPctRep = congressData.housePctRep
        sPctDem = congressData.senatePctDem
        sPctRep = congressData.senatePctRep
        presParty = congressData.presParty
        print 'president party: ' + str(presParty)
        partyControl = 0
        if (hPctDem > hPctRep and sPctDem > sPctRep):
            partyControl = 1
        elif (hPctDem < hPctRep and sPctDem < sPctRep):
            partyControl = -1
        # assign features and labels  
        label = -1 # other
        if bill.succeeded():
            label = 1
        elif bill.failed():
            label = 0
        else:
            continue
        catNum = catMap[bill.category]

        # once you add in a categorical feature, definitely want classifier without distance metric
        X[thisRow, :] = [bill.cosponsorCount, bill.pctDemCosponsors, bill.pctRepCosponsors, catNum, partyControl, presParty]
        y[thisRow] = label
        z[thisRow] = int(bill.congress)
        thisRow += 1
    return(X,y,z)

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
    (X,y,z) = getFeatures(bills)
    print 'Got data with: ' + str(len(X[:,0])) + ' observations'
    getPassedPercent(y)
    
    # try kfolds
    crossValidate(X,y)
    
    # look at feature distributions
    labels = ['Number of cosponsors', '% Democratic Cosponsors', '% Republican Cosponsors', 'Numerical Category', 'Party Control', 'President Party']
    getFeatureDistributions(X, labels)
    
    # train, leaving out most recent congress (113), and get confusion matrix
    cm = trainAndTest(X,y,z)
    targetNames = ['fail', 'pass']
    plotConfusionMatrix(cm, targetNames)

if __name__ == "__main__":
    main()
