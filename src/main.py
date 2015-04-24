# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:07:11 2015
Data Science Final Project 
@author: j_ast_000
"""

import json
import os
import glob
import pandas
import numpy as np

'''
A simple class used to represent the state of a bill or resolution
'''
class Bill:
    class Status:
        enacted, passed, failed, ammended, vetoed, other = range(6)
    
    def __init__(self):
        self.status = Status.other  
        
    def __init__(self, s):
        self.status = s
    
    def succeeded():
        if self.status == enacted or self.status == passed:
            return True 
        else:
            return False      
    

'''
Returns a dict of congresspeoples' names -> parties
'''
def getLegislators():
    # build local database of congresspeople
    # TODO: make sure there are not duplicates
    nameToParty = {}  
    prefix = '../legislators/'
    dataDirs = os.path.join(prefix, '*')
    filepaths = list(set(glob.glob(dataDirs)))    
    for f in filepaths:   
        df = pandas.read_csv(f)
        lastNames = list(df['last_name'])
        firstNames = list(df['first_name'])
        parties = list(df['party'])
        for i in range(len(lastNames)):
            fullName = lastNames[i] + ', ' + firstNames[i]
            party = parties[i]
            nameToParty[fullName] = party;   
    return nameToParty
    
'''
Returns a list of all the paths to files containing bill json data
'''
def getBillFilePaths():
    # build a list of all the json files containing bill data
    prefix = '../bills/'
    dataDirs = os.path.join(prefix, '*')
    directory_names = list(set(glob.glob(dataDirs)))       
    filepaths = []
    for folder in directory_names:       
        for subfolder in os.walk(folder):
            dirname = subfolder[0]
            for f in subfolder[2]:  
                if (str(f) == 'data.json'):
                    path = os.path.join(dirname, f)
                    filepaths.append(path)
    return filepaths
    

def main():
    print "Welcome to my data science project" 
    numFeats = 3
    featNames = ['cosponsorCount', 'percentDem', 'percentInd']  
    
    nameToParty = getLegislators()
    filepaths = getBillFilePaths()
    
    # X contains features, y contains targets
    numRows = len(filepaths)
    X = np.zeros((numRows, numFeats), dtype=float)  
    y = np.zeros((numRows, 1), dtype=int)
    
    # extract features from list of bills
    # we probably only care about bills and joint resolutions
    # not simple or concurrent resolutions that only affect congress
    thisRow = 0
    skippedRows= 0
    statusCounts = {}
    monthCounts = {}
    for path in filepaths:    
        jfile = open(path, 'r+')            
        json_data = jfile.read().decode("utf-8")
        jdata = json.loads(json_data)

        # FEATURES
        #summary = jdata['summary']['text']
        cosponsors = []
        if 'cosponsors' in jdata:
            cosponsors = jdata.get('cosponsors')

        status = jdata['status']
        if status not in statusCounts:
            statusCounts[status] = 1
        else:
            statusCounts[status] +=1
        csCount = 0
        csDems = 0
        csInds = 0
        pctDems = 0
        pctInds = 0
        
        for cs in cosponsors:
            name = cs['name']
            if name not in nameToParty:
                continue
            csCount += 1
            party = nameToParty[name]
            if party == 'Democrat':
                csDems += 1
            elif party == 'Independent':
                csInds += 1
        
        if csCount > 0:
            pctDems = csDems * 1.0 / csCount
            pctInds = csInds * 1.0 / csCount
        '''
        # LABELS
        actions = jdata['actions'] 
        for action in actions:
            if 'result' in action:
                print action['result']
        '''
        # assign features and labels  
        X[thisRow, :] = [csCount, pctDems, pctInds]
        y[thisRow] = 1#label;
        
        date = jdata['introduced_at'] #ie "2013-01-23", 
        year = date[0:4]
        month = date[5:7]
        dateKey = ''
        if month < 10:
            dateKey = year + '.0' + month
        else:
            dateKey = year + '.' + month
        if dateKey not in monthCounts:
            monthCounts[dateKey] = 1
        else:
            monthCounts[dateKey] +=1
                         

        thisRow += 1
        jfile.close()

    print '================== SUMMARY: =================='
    print 'Status counts:'
    print statusCounts
    for stat in statusCounts:
        pct = statusCounts[stat] * 1.0 / len(filepaths)
        print 'Status: ' + stat + ' pct: ' + str(pct)
        
#    print 'Month counts:'
#    keyList = sorted(list(monthCounts.keys()))
#    for k in keyList:
#        print k + ': ' + str(monthCounts[k])
        
    print 'Skipped ' + str(skippedRows) + ' rows due to missing keys'      
    

if __name__ == "__main__":
    main()
