# -*- coding: utf-8 -*-
"""
Created on Wed May 06 19:23:35 2015

@author: j_ast_000
"""
import json
import os
import glob
import pandas
import numpy as np
import pickle
import datetime 

'''
Class used to represent the state of a bill or resolution
'''
class Bill:       
    def __init__(self, stat, cat, csCount, pctDem, pctRep, date, congress):
        self.status = stat
        self.category = cat
        self.cosponsorCount = csCount
        self.pctDemCosponsors = pctDem
        self.pctRepCosponsors = pctRep
        self.date = date
        self.congress = congress
    
    def succeeded(self):
        if self.status == 'PASSED:BILL' \
        or self.status == 'ENACTED:VETO_OVERRIDE' \
        or self.status == 'ENACTED:SIGNED':
            return True 
        else:
            return False   
            
    def failed(self):
        if self.status == 'PROV_KILL:SUSPENSIONFAILED' \
        or self.status == 'PROV_KILL:CLOTUREFAILED' \
        or self.status == 'PROV_KILL:VETO' \
        or self.status == 'VETOED:POCKET' \
        or self.status == 'VETOED:OVERRIDE_FAIL_ORIGINATING:HOUSE' \
        or self.status == 'VETOED:OVERRIDE_FAIL_ORIGINATING:SENATE' \
        or self.status == 'FAIL:SECOND:SENATE' \
        or self.status == 'FAIL:SECOND:HOUSE' \
        or self.status == 'FAIL:ORIGINATING:HOUSE' \
        or self.status == 'FAIL:ORIGINATING:SENATE':
            return True 
        else:
            return False   
 
class Congress:
    def __init__(self, num, housePctDem, housePctRep, senatePctDem, senatePctRep, presParty):
        self.number = num
        self.housePctDem = housePctDem
        self.housePctRep = housePctRep
        self.senatePctDem = senatePctDem
        self.senatePctRep = senatePctRep
        self.presParty = presParty
        

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
    
def getPartiesByCongress():
    d = {}
    filename = '../partyControl.csv'
    df = pandas.read_csv(filename)    
    congressNums = list(df['Congress'])
    senateDemNums = list(df['Senate Dems'])
    houseDemNums = list(df['House Dems'])
    senateRepNums = list(df['Senate Reps'])
    houseRepNums = list(df['House Reps'])
    presParties = list(df['President Party'])
    for i in range(len(congressNums)):
        num = congressNums[i]
        hPctDem = float(houseDemNums[i]) / 435
        hPctRep = float(houseRepNums[i]) / 435
        sPctDem = float(senateDemNums[i]) / 100
        sPctRep = float(senateRepNums[i]) / 100
        presPartyCode = presParties[i]
        presParty = 0
        if (presPartyCode == 'D'):
            presParty = 1
        congress = Congress(num, hPctDem, hPctRep, sPctDem, sPctRep, presParty)
        d[num] = congress
    return d
        
    
def loadData(pickleFileName):
    numFeats = 4
    bills = {}
    
    nameToParty = getLegislators()
    filepaths = []
    for congressNum in range(100,113):
        filepaths.extend(getBillFilePaths(congressNum))
        #votepaths = getVoteFilePaths(congressNum)
    
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
    procCount = 0
    for path in filepaths:    
        procCount += 1
        if procCount % 10000 == 0:
            print 'Processed ' + str(procCount) + ' bills'
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

        congress = jdata['congress']
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
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[8:10])
        date = datetime.date(year, month, day)
        dateKey = ''
        if month < 10:
            dateKey = str(year) + '.0' + str(month)
        else:
            dateKey = str(year) + '.' + str(month)
        if dateKey not in monthCounts:
            monthCounts[dateKey] = 1
        else:
            monthCounts[dateKey] +=1
        
        # assign features and labels
        bill = Bill(status, category, csCount, pctDems, pctReps, date, congress)
        label = -1 # other
        if bill.succeeded() == False and bill.failed() == False:
            continue
        bills[billId] = bill
        jfile.close()
        
        trainingSampleCount += 1

    print '================== DATA GATHERING SUMMARY: =================='
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
    
    #Create a DataFrame object to make subsetting the data on the class 
    pickleFile = open(pickleFileName, 'wb')
    pickle.dump(bills, pickleFile)