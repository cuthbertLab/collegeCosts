# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         collegeCosts.py
# Purpose:      System for searching college costs by income levels
#
# Authors:      Michael Scott Cuthbert
#
# Copyright:    Copyright © 2016 Michael Scott Cuthbert and cuthbertLab
# License:      MIT, see LICENSE file
#-------------------------------------------------------------------------------
'''
System for searching college costs by income levels
'''

from __future__ import division, print_function

import csv
import codecs

def readFile():
    '''
    college.csv is the data from collegescorecard.ed.gov/data called "Scorecard data"
    https://s3.amazonaws.com/ed-college-choice-public/Most+Recent+Cohorts+(Scorecard+Elements).csv
    '''
    fn = 'college.csv'
    header = []
    rows = []
    
    with codecs.open(fn, encoding='latin-1') as csvfile: # encoding is guessed, but appears right
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                rows.append(School(row, header))

    return rows

class School(object):
    def __init__(self, r, h):
        self.data = r
        self.headers = h

    @property
    def isFourYear(self):
        if self.preddeg == 3: # 1 = cert; 2 = community; 4 = grad only
            return True
        return False

    @property
    def isPublic(self):
        if self.control == 1:
            return True
        return False

    @property
    def isPrivate(self): # control == 3 means forProfit?
        if self.control == 2:
            return True
        return False

    @property
    def SAT(self):
        sat = {'v25': None, 'v50': None, 'v75': None,
               'm25': None, 'm50': None, 'm75': None}
        sat['v25'] = self.satvr25
        sat['v50'] = self.satvrmid
        sat['v75'] = self.satvr75
        sat['m25'] = self.satmt25
        sat['m50'] = self.satmtmid
        sat['m75'] = self.satmt75
        return sat
    
    @property
    def sat25(self):
        '''
        If there is any SAT score reported, return the 25th percentile combined.
        If 25th percentile is reported, use that.  Otherwise use 89.5% of midpoint,
        which is the average across all data
        '''
        sats = self.SAT
        if sats['v50'] is None:
            return None
        if sats['v25'] is not None and sats['m25'] is not None:
            return sats['v25'] + sats['m25']
        else:
            return .895 * (sats['v25'] + sats['m25'])
    
    @property
    def gradRate(self):
        gr = self.C150_4_POOLED_SUPP
        if gr is None:
            gr = self.C200_L4_POOLED_SUPP
        if gr is None:
            return None
        try:
            return float(gr)
        except ValueError:
            return None
    
    def cost(self, level=None):
        '''
        cost at various levels.  level == None, avg for all aid.
        1 = 0-30k, 2=30k-48, 3=48-75k, 4=75-110; 5=110+
        '''
        levPrefix = 'NPT4'
        if self.isPublic:
            levSuffix = '_PUB'
        else:
            levSuffix = '_PRIV'
        
        if level is not None:
            levPrefix += str(level)
        
        lColumn = levPrefix + levSuffix
        return getattr(self, lColumn)
    
    def __getattr__(self, attr):
        found = None
        i = 0
        for i, h in enumerate(self.headers):
            if h.lower() == attr.lower():
                found = i
                break
        if found is None:
            raise AttributeError("Row has no column %r" % attr)
        d = self.data[i]
        if d == 'NULL':
            return None
        try:
            junk_intD = int(d) # catch value error.
            if int(d) == float(d):
                return int(d)
            else:
                return float(d)
        except ValueError:
            return d

def getSAT25diff(rows):
    '''
    get the multiplier for SAT50 to get SAT25 on average, to sort schools that do not report.
    On average it's .895, will use .895 for each (it's .894 for each one separate, showing that
    they're not too correlated)
    '''
    satScores = []
    for r in rows:
        sat = r.SAT
        if sat['v25'] is None or sat['m25'] is None:
            continue
        satDiffs = sat['v25'] + sat['m25']
        satRatio = satDiffs/(sat['v50'] + sat['m50'])
        satScores.append(satRatio)
    return sum(satScores)/len(satScores), satScores


def filterRows(rows, satMin=700, satMax=800, costMax=10000, costLevel=1):
    rOut = []
    for r in rows:
        if r.gradRate is None or r.gradRate < .34:
            continue
        if r.isPublic is False and r.isPrivate is False:
            continue
        if r.isFourYear is not True:
            continue
        if r.sat25 is None:
            continue
        if (r.sat25 < satMin or r.sat25 > satMax):
            continue
        c = r.cost(costLevel)
        if c is None:
            continue
        if c > costMax:
            continue
        rOut.append(r)
    
    rOut.sort(key=lambda r: r.cost(costLevel))
    return rOut

def generateSimulation(costLevel=1, costMax=10000, pubStateOnly=''):
    r = readFile()
    
    for satMin in range(700, 1500, 100):
        print("\n\n*****************     SAT 25th percentile of", satMin, "to", satMin+100, 
              "    ***************\n")
        rOut = filterRows(r, satMin=satMin, satMax=satMin+100, costMax=costMax, costLevel=costLevel)
        for rr in rOut:
            pub = ""
            if rr.isPublic:
                if rr.STABBR != pubStateOnly:
                    continue
                pub = "*" + rr.STABBR
            print("%50s $%5d SAT:%4d, Grad: %2d%% %4s" % 
                  (rr.instnm[0:50], rr.cost(costLevel), rr.sat25, int(rr.gradRate*100), pub))
            

if __name__ == '__main__':
    generateSimulation(1, 10000, 'MA')
