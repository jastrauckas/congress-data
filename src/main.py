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
import pickle

'''
A simple class used to represent the state of a bill or resolution
'''
class Bill:       
    def __init__(self, stat, cat, pctDem, pctRep):
        self.status = stat
        self.category = cat
        self.pctDemCosponsors = pctDem
        self.pctRepCosponsors = pctRep
    
    def succeeded(self):
        if self.status == 'PASSED:BILL' \
        or self.status == 'ENACTED:SIGNED':
            return True 
        else:
            return False   
            
    def failed(self):
        if self.status == 'PROV_KILL:SUSPENSIONFAILED' \
        or self.status == 'PROV_KILL:CLOTUREFAILED' \
        or self.status == 'FAIL:SECOND:SENATE' \
        or self.status == 'FAIL:SECOND:HOUSE' \
        or self.status == 'FAIL:ORIGINATING:HOUSE' \
        or self.status == 'FAIL:ORIGINATING:SENATE':
            return True 
        else:
            return False   
        

class Vote:
    def __init__(self):
        self.made = True

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
def getBillFilePaths(congressNum):
    # build a list of all the json files containing bill data
    prefix = '../data/' + str(congressNum) + '/bills'
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
    
'''
Returns a list of all the paths to files containing bill json data
'''
def getVoteFilePaths(congressNum):
    # build a list of all the json files containing bill data
    prefix = '../data/' + str(congressNum) + '/votes'
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
    bills = {}
    
    nameToParty = getLegislators()
    filepaths = []
    for congressNum in range(100,113):
        filepaths.extend(getBillFilePaths(congressNum))
        #votepaths = getVoteFilePaths(congressNum)
    
    # X contains features, y contains targets
    numRows = len(filepaths)
    X = np.zeros((numRows, numFeats), dtype=float)  
    y = np.zeros((numRows, 1), dtype=int)
    
    # extract features from list of bills
    # we probably only care about bills and joint resolutions
    # not simple or concurrent resolutions that only affect congress
    # also skip anything that has neither passed nor failed
    thisRow = 0
    skippedRows= 0
    trainingSampleCount = 0
    statusCounts = {}
    monthCounts = {}
    
    # what information do i need from the bill?
    for path in filepaths:    
        jfile = open(path, 'r+')            
        json_data = jfile.read().decode("utf-8")
        jdata = json.loads(json_data)

        # FEATURES
        #summary = jdata['summary']['text']
        cosponsors = []
        if 'cosponsors' in jdata:
            cosponsors = jdata.get('cosponsors')
        billId = jdata.get('bill_id')
        category = jdata.get('subjects_top_term')

        status = jdata['status']
        if status not in statusCounts:
            statusCounts[status] = 1
        else:
            statusCounts[status] +=1
        csCount = 0
        csDems = 0
        csInds = 0
        pctDems = 0
        pctReps = 0
        
        for cs in cosponsors:
            name = cs['name']
            if name not in nameToParty:
                continue
            csCount += 1
            party = nameToParty[name]
            if party == 'Democrat':
                csDems += 1
            elif party == 'Republican':
                csInds += 1
        
        if csCount > 0:
            pctDems = csDems * 1.0 / csCount
            pctReps = csInds * 1.0 / csCount
        '''
        '''
        
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
                         
        bill = Bill(status, category, pctDems, pctReps)
        bills[billId] = bill
        thisRow += 1
        jfile.close()
        
        # assign features and labels  
        label = -1 # other
        if bill.succeeded():
            label = 1
        elif bill.failed():
            label = 0
        else:
            continue
        
        trainingSampleCount += 1
        X[thisRow, :] = [csCount, pctDems, pctReps]
        y[thisRow] = label

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
    print 'Got ' + str(trainingSampleCount) + ' training samples'
    

if __name__ == "__main__":
    main()
