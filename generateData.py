# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         generateData.py
# Purpose:      Make the data work...
#
# Authors:      Michael Scott Cuthbert
#
# Copyright:    Copyright © 2016 Michael Scott Cuthbert and cuthbertLab
# License:      MIT, see LICENSE file
#-------------------------------------------------------------------------------
'''
generates the HTML Files
'''
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

import collegeCosts as cc

states = {
        'AK': 'Alas[ka]',
        'AL': 'Ala[bama]',
        'AR': '[Ark]ansas',
        'AS': 'American[Samoa]',
        'AZ': 'Ari[zona]',
        'CA': '[Cali]fornia',
        'CO': 'Col[o]rado',
        'CT': '[Conn]ecticut',
        'DC': 'Washington[DC]',
        'DE': '[Del]aware',
        'FL': '[Flor]ida',
        'GA': 'Ge[or]gia',
        'GU': 'Guam',
        'HI': 'Ha[wai]i',
        'IA': 'I[o]wa',
        'ID': '[Ida]ho',
        'IL': 'Illi[nois]',
        'IN': 'Ind[iana]',
        'KS': '[Kan]sas',
        'KY': 'Ken[tucky]',
        'LA': '[Lou]isiana',
        'MA': '[Mass]achusetts',
        'MD': 'Mary[land]',
        'ME': 'Maine',
        'MI': 'Michi[gan]',
        'MN': 'Minne[sota]',
        'MO': 'Mis[souri]',
        'MP': 'N.Mariana[Islands]',
        'MS': '[Miss]issippi',
        'MT': 'Mon[tana]',
        'NC': 'North[Carolina]',
        'ND': 'North[Dakota]',
        'NE': 'Nebraska',
        'NH': 'New[Hampshire]',
        'NJ': 'New[Jersey]',
        'NM': 'New[Mexico]',
        'NV': 'Neva[da]',
        'NY': 'New[York]',
        'OH': 'O[hi]o',
        'OK': '[Ok]lahoma',
        'OR': '[Ore]gon',
        'PA': '[Penn]sylvania',
        'PR': 'Puerto[Rico]',
        'RI': 'Rhode[Island]',
        'SC': 'South[Carolina]',
        'SD': 'South[Dakota]',
        'TN': '[Tenn]essee',
        'TX': '[Tex]as',
        'UT': '[U]tah',
        'VA': '[Vir]ginia',
        'VI': 'Virgin[Islands]',
        'VT': 'Ver[mont]',
        'WA': 'Washing[ton]',
        'WI': '[Wisc]onsin',
        'WV': 'West[Virginia]',
        'WY': '[Wyo]ming',
        None: 'College[Costs]'
}

stateNames = {}
for abbrev in states:
    newState = states[abbrev].replace('[', '<span class="accent">').replace(']', '</span>')
    stateNames[abbrev] = newState

del(states)

satRanges = [(400, 800, "SAT 25th percentile below 800"),
             (800, 900, "SAT 25th percentile 800 to 899"),
             (900, 1000, "SAT 25th percentile 900 to 999"),
             (1000, 1100, "SAT 25th percentile 1000 to 1099"),
             (1100, 1200, "SAT 25th percentile 1100 to 1199"),
             (1200, 1350, "SAT 25th percentile 1200 to 1349"),
             (1350, 1601, "SAT 25th percentile above 1350"),
             (None, None, "Without SAT Data"),
             ]

actRanges = [(2, 18, "ACT 25th percentile: 17 or below"),
             (18, 20, "ACT 25th percentile: 18 or 19"),
             (20, 22, "ACT 25th percentile: 20 or 21"),
             (22, 24, "ACT 25th percentile: 22 or 23"),
             (24, 27, "ACT 25th percentile: 24, 25, or 26"),
             (27, 31, "ACT 25th percentile: 27 to 30"),
             (31, 37, "ACT 25th percentile: 31 or higher"),
             (None, None, "Without ACT Data"),
             ]



class FileGenerator:
    yearStr = '2016'
    outdir = 'data/'
    dataTemplateFile = 'dataTemplate.html'
    markPub = '*Pub:'

    def __init__(self):
        self.r = cc.readFile()
        self.template = "{dataGoesHere}"
        self.quiet = False
        self.cachedInfo = {}

        self.getTemplate()
        
    def getTemplate(self):
        with open(self.dataTemplateFile) as dtf:
            self.template = ''.join(dtf.readlines())
    
    def outFilePath(self, incomeLevel, stateAbbr, testType='SAT'):
        stateAbbrStr = str(stateAbbr) # for "None"
        if testType == 'SAT':
            testType = ''
        outfp = self.outdir + self.yearStr + "_" + stateAbbrStr + str(
                                                            incomeLevel) + testType + '.html'
        return outfp

    def oneLink(self, row, incomeLevel=5, testType='SAT'):
        pub = ""
        if row.isPublic:
            pub = self.markPub + row.STABBR
        
        shortName = row.shortName(30)
        testScore = row.sat25 if testType == 'SAT' else row.act25
        
        
        costStr =  locale.format("%d", row.cost(incomeLevel), grouping=True)
        out = ("  $%7s   %4s    %3d%% %7s" % 
              (costStr, testScore, int(row.gradRate*100), pub))
        out = ('<a target=_new href="https://collegescorecard.ed.gov/school/?%d">%30s</a>  %s' %
               (row.unitid, shortName, out))
        return out
    

    def generateOneTestHeader(self, incomeLevel, testExplain):
        '''
        this used to be complex enough to warrant its own method...
        '''
        header = "<h2>" + testExplain + "</h2>\n" 
        return header
    
    def generateOneTestRange(self, incomeLevel, testData, testType='SAT'):
        testMin, testMax, testExplain = testData # unpack them tuples
        header = self.generateOneTestHeader(incomeLevel, testExplain)

        out = []
        out.append(header)
        out.append("<pre class='cost'>")
        if testType == 'SAT':
            out.append("<b>                                         Cost     SAT     Grad            </b>")
            rOut = cc.filterRows(self.r, 
                     satMin=testMin, 
                     satMax=testMax, 
                     costMax=None, 
                     costLevel=incomeLevel,
                     )

        elif testType == 'ACT':
            out.append("<b>                                         Cost     ACT     Grad            </b>")
            rOut = cc.filterACTRows(self.r, 
                                 actMin=testMin, 
                                 actMax=testMax, 
                                 costMax=None, 
                                 costLevel=incomeLevel,
                                 )
        
        
        for rr in rOut:
            if rr.belowCostLevel(incomeLevel):
                out.append(self.oneLink(rr, incomeLevel, testType))
        
        out.append("</pre>")
        
        moreExpensiveExists = False
        moreExpensive = []
        moreExpensive.append("<button class='btn btn-default btn-lg btn-showCost' id='" +
                    str(incomeLevel) + "_" + str(testMin) + "'>Show More Expensive</button>")
        moreExpensive.append('<pre class="cost hiddenPre" id="pre' + str(incomeLevel) + "_" + 
                             str(testMin) + '">')
        for rr in rOut:
            if not rr.belowCostLevel(incomeLevel) and rr.belowExtremeCostLevel(incomeLevel):
                moreExpensive.append(self.oneLink(rr, incomeLevel, testType))
                moreExpensiveExists = True
            elif not rr.belowExtremeCostLevel(incomeLevel):
                moreExpensive.append("<span class='danger'>" + self.oneLink(rr, incomeLevel, testType) + "</span>")
                moreExpensiveExists = True
        moreExpensive.append("</pre>")
        
        if moreExpensiveExists:
            out.extend(moreExpensive)        
        out.append("&nbsp;<br>&nbsp;<br>&nbsp;<br>")
        
        return out

    def stateFilteredTestRange(self, incomeLevel, stateAbbr, testData, testType='SAT'):
        cacheKey = (incomeLevel, testData, testType)
        if cacheKey in self.cachedInfo:
            allRows = self.cachedInfo[cacheKey][:]
        else:
            allRows = self.generateOneTestRange(incomeLevel, testData, testType)
            self.cachedInfo[cacheKey] = allRows[:]
        
        filteredRows = []
        stateMark = ""
        if stateAbbr is not None:
            stateMark = self.markPub + stateAbbr
        for r in allRows:
            if stateAbbr is not None and self.markPub in r and stateMark not in r:
                continue
            if stateAbbr is not None and stateMark in r:
                r = r.replace(stateMark, '(publ.)')
            elif stateAbbr is None and self.markPub in r:
                r = r.replace(self.markPub, '    *')
                
            filteredRows.append(r)

        return '\n'.join(filteredRows)
        
    
    def generateOneFile(self, incomeLevel=1, stateAbbr='', testType='SAT'):
        if self.quiet is not True:
            print("Generating: ", stateAbbr, incomeLevel, testType)
        outFilePath = self.outFilePath(incomeLevel, stateAbbr, testType)     
        
        allRanges = []
        if testType == 'SAT':
            testRanges = satRanges
        else:
            testRanges = actRanges
        
        for testData in testRanges:
            oneRangeStr = self.stateFilteredTestRange(incomeLevel, stateAbbr, testData, testType)
            allRanges.append(oneRangeStr)
        
        allAllStr = '\n'.join(allRanges)
        abbrevNice = stateAbbr
        if abbrevNice is None:
            abbrevNice = 'All US'
        writeOut = self.template.format(dataGoesHere=allAllStr,
                                        stateAbbr=abbrevNice,
                                        stateName=stateNames[stateAbbr],
                                        incomeLevel=cc.incomeLevels[incomeLevel])
        with open(outFilePath, 'w', encoding='utf-8') as ofp:
            ofp.write(writeOut)
    
    
    def generateAll(self):
        for testType in ('ACT', 'SAT'):
            for incomeLevel in range(1, 6):
                for stateAbbr in cc.stateList:
                    self.generateOneFile(incomeLevel, stateAbbr, testType)
            
if __name__ == '__main__':
    fg = FileGenerator()
    fg.generateAll()
    #fg.generateOneFile(2, None)
            
