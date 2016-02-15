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

stateList = [l.upper() for l in ("al ak az ar ca co ct dc de fl ga hi id il in ia ks " + 
    "ky la me md ma mi mn ms mo mt ne nv nh nj nm ny nc nd oh ok or pa " + 
    "pr ri sc sd tn tx ut vt va vi wa wv wi wy " + 
    "dc vi pr").split()]
stateList.append(None)


incomeLevels = [None, 
                'below $30,000', 
                'from $30,001 to $48,000', 
                'from $48,001 to $75,000', 
                'from $75,001 to $110,000',
                'of $110,001 and above']

costCutoffs = [None, 10000, 16000, 25000, 35000, 55000, 80000]


def readFile():
    '''
    college.csv is the data from collegescorecard.ed.gov/data called "Scorecard data"
    https://s3.amazonaws.com/ed-college-choice-public/Most+Recent+Cohorts+(Scorecard+Elements).csv
    '''
    fn = 'college.csv'
    header = []
    rows = []
    
    with codecs.open(fn, encoding='latin-1') as csvfile: # encoding is guessed, but appears right
        reader = csv.reader(csvfile)      # King's college or something is wrong...
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                rows.append(School(row, header))

    return rows

class School(object):
    '''
    Takes in one school information object from the CSVfile...
    '''
    def __init__(self, r, h):
        self.data = r
        self.headers = h
        self.attrCache = {}

    def __repr__(self):
        return "<%s.%s %s>" % (self.__module__, self.__class__.__name__, 
                                  self.instnm[0:40])

    def __getattr__(self, attr):
        if attr not in self.attrCache:
            self.attrCache[attr] = self._getattrHelper(attr)
        return self.attrCache[attr]

    def _getattrHelper(self, attr):            
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
            # apparently never used; the government might calculate 25th p. always?
            return .895 * (sats['v50'] + sats['m50'])


    @property
    def act25(self):
        if self.ACTCM25 is not None:
            return self.ACTCM25
        # every school with no ACTCM25 also lacks ACTCMMID so don't look there.
        
    
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
    
    def belowCostLevel(self, level):
        c = self.cost(level)
        if c <= costCutoffs[level]:
            return True
        else:
            return False

    def belowExtremeCostLevel(self, level):
        c = self.cost(level)
        if c <= costCutoffs[level + 1]:
            return True
        else:
            return False


    knownAbbreviations = {
        'Massachusetts Institute of Technology': 'MIT',
        'Columbia University in the City of New York': 'Columbia (NYC)',
        'California Institute of Technology': 'Caltech',                
        'Cooper Union for the Advancement of Science and Art': 'Cooper Unison',
        'Virginia Polytechnic Institute and State University': 'Virginia Polytechnic',
        'Louisiana State University and Agricultural & Mechanical College': 'LSU, A&M',
        'Saint Charles Borromeo Seminary-Overbrook': 'St. Ch. Borromeo Sem.-Overbrook',
    }
    
    def shortName(self, maxLen=30):
        def big():
            return (len(shortName) > maxLen)
        shortName = self.instnm
        if shortName in self.knownAbbreviations:
            shortName = self.knownAbbreviations[shortName]
            
        if big():
            shortName = shortName.replace('San Francisco', 'SF')
        if big():
            shortName = shortName.replace('United States', 'US')
        if big():
            shortName = shortName.replace('California State University-', 'CSU ')
        if big():
            shortName = shortName.replace('Inter American University of Puerto Rico', 'Inter Amer U. PR')

        if big():
            shortName = shortName.replace('California Polytechnic State University-', 'Cal Poly ')
        if big():
            # these have "-Penn State...' after them so redundant
            shortName = shortName.replace('Pennsylvania State University-', '')
        if big():
            shortName = shortName.replace('North Carolina State University', 'NC State')
        if big():
            shortName = shortName.replace('niversity', 'niv.').replace('ollege', 'ol.').replace(
                                                            'Theological Seminary', 'Seminary')
        if big():
            shortName = shortName.replace(' at ', ' ')
        if big():
            shortName = shortName.replace('niv.', '.').replace('ol.', '.').replace(
                                                                        'Universidad ', 'U.')
        if big():
            shortName = shortName.replace('Institute', 'Inst.')
        if big():
            shortName = shortName.replace('California', 'Cal.')
        if big():
            shortName = shortName.replace('Campuses ', ' ').replace('Campuses', '')
        if big():
            shortName = shortName.replace('Campus ', ' ').replace('Campus', '')
        if big():
            shortName = shortName.replace('the ', '').replace('The ', '')
        if big():
            shortName = shortName.replace('Conservatory', 'Conserv.')
        if big():
            shortName = shortName.replace('Technology', 'Tech.')
        if big():
            shortName = shortName.replace('Saint', 'St.')
        if big():
            shortName = shortName.replace('School of ', '')
        if big():
            shortName = shortName.replace('School', '')
        if big():
            shortName = shortName.replace('Sciences', '')
        if big():
            shortName = shortName.replace('Science', '')
        if big():
            shortName = shortName.replace('of ', '')
        if big():
            shortName = shortName.replace('Seminary', 'Sem.')
        if big():
            shortName = shortName.replace('and ', '& ')
        if big():
            shortName = shortName.replace('Southern ', 'S. ')
        if big():
            shortName = shortName.replace(' & ', '&')

        shortName = shortName.replace('  ', ' ')
        
        if big():
            shortName = shortName[0:maxLen]
            #print(shortName, '          ', self.instnm)
        shortName = shortName.strip()
            
        return shortName


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


def filterRows(rows, satMin=700, satMax=800, costMax=None, costLevel=1, stateAbbr=None):
    rOut = []
    for r in rows:
        if r.gradRate is None or r.gradRate < .333333:
            continue
        if r.isPublic is False and r.isPrivate is False:
            continue
        if r.isFourYear is not True:
            continue
        if satMin is not None and r.sat25 is None:
            continue
        if (satMin is not None and satMax is not None and r.sat25 is not None and 
                (r.sat25 < satMin or r.sat25 >= satMax)):
            continue
        if satMin is None and r.sat25 is not None:
            continue
        c = r.cost(costLevel)
        if c is None:
            continue
        if costMax is not None and c > costMax:
            continue
        if stateAbbr is not None and r.isPublic and r.STABBR != stateAbbr:
            continue
        
        rOut.append(r)
    
    rOut.sort(key=lambda r: r.cost(costLevel))
    return rOut

def filterACTRows(rows, actMin=700, actMax=800, costMax=None, costLevel=1, stateAbbr=None):
    rOut = []
    for r in rows:
        if r.gradRate is None or r.gradRate < .333333:
            continue
        if r.isPublic is False and r.isPrivate is False:
            continue
        if r.isFourYear is not True:
            continue
        if actMin is not None and r.act25 is None:
            continue
        if (actMin is not None and actMax is not None and r.act25 is not None and 
                (r.act25 < actMin or r.act25 >= actMax)):
            continue
        if actMin is None and r.act25 is not None:
            continue
        c = r.cost(costLevel)
        if c is None:
            continue
        if costMax is not None and c > costMax:
            continue
        if stateAbbr is not None and r.isPublic and r.STABBR != stateAbbr:
            continue
        
        rOut.append(r)
    
    rOut.sort(key=lambda r: r.cost(costLevel))
    return rOut


def generateSimulation(costLevel=1, costMax=10000, pubStateOnly=''):
    r = readFile()
    
    for satMin in range(700, 1500, 100):
        satMax = satMin + 99
        print("\n\n*****************     SAT 25th percentile of", satMin, "to", satMax, 
              "    ***************\n")
        rOut = filterRows(r, satMin=satMin, satMax=satMax, costMax=costMax, costLevel=costLevel)
        for rr in rOut:
            pub = ""
            if rr.isPublic:
                if rr.STABBR != pubStateOnly and pubStateOnly is not None:
                    continue
                pub = "*" + rr.STABBR
            print("%50s $%5d SAT:%4d, Grad: %2d%% %4s" % 
                  (rr.instnm[0:50], rr.cost(costLevel), rr.sat25, int(rr.gradRate*100), pub))
            

if __name__ == '__main__':
    generateSimulation(1, 10000, None)
    print(stateList)
