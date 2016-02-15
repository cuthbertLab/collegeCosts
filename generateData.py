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
        'MO': 'Missou[ri]',
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
    
    def outFilePath(self, incomeLevel, stateAbbr):
        stateAbbrStr = str(stateAbbr) # for "None"
        outfp = self.outdir + self.yearStr + "_" + stateAbbrStr + str(incomeLevel) + '.html'
        return outfp

    def oneLink(self, row, incomeLevel=5):
        pub = ""
        if row.isPublic:
            pub = self.markPub + row.STABBR
        
        shortName = row.instnm
        if len(shortName) > 30:
            shortName = shortName.replace('California State University-', 'CSU ').replace(
                                    'niversity', 'niv.').replace('ollege', 'ol.')
        if len(shortName) > 30:
            shortName = shortName.replace('niv.', '.').replace('ol.', '.')
        if len(shortName) > 30:
            shortName = shortName[0:30]
            
        costStr =  locale.format("%d", row.cost(incomeLevel), grouping=True)
        out = ("  $%7s   %4d     %2d%% %7s" % 
              (costStr, row.sat25, int(row.gradRate*100), pub))
        out = ('<a href="https://collegescorecard.ed.gov/school/?%d">%30s</a>  %s' %
               (row.unitid, shortName, out))
        return out
    

    def generateOneSatHeader(self, incomeLevel, satMin, satMax):
        header = "<h2>SAT 25th percentile of " + str(satMin) + " to " + str(satMax) + "</h2>\n" 
        return header
    
    def generateOneSatRange(self, incomeLevel, satMin, satMax=None):
        if satMax is None:
            satMax = satMin + 99
        
        header = self.generateOneSatHeader(incomeLevel, satMin, satMax)

        out = []
        out.append(header)
        out.append("<pre class='cost'>")
        out.append("<b>                                         Cost     SAT     Grad            </b>")

        rOut = cc.filterRows(self.r, 
                             satMin=satMin, 
                             satMax=satMax, 
                             costMax=None, 
                             costLevel=incomeLevel,
                             )
        
        
        for rr in rOut:
            if rr.belowCostLevel(incomeLevel):
                out.append(self.oneLink(rr, incomeLevel))
        
        out.append("</pre>")
        
        moreExpensiveExists = False
        moreExpensive = []
        moreExpensive.append("<button class='btn btn-default btn-lg btn-showCost' id='" +
                    str(incomeLevel) + "_" + str(satMin) + "'>Show More Expensive</button>")
        moreExpensive.append('<pre class="cost hiddenPre" id="pre' + str(incomeLevel) + "_" + str(satMin) + '">')
        for rr in rOut:
            if not rr.belowCostLevel(incomeLevel) and rr.belowExtremeCostLevel(incomeLevel):
                moreExpensive.append(self.oneLink(rr, incomeLevel))
                moreExpensiveExists = True
            elif not rr.belowExtremeCostLevel(incomeLevel):
                moreExpensive.append("<span class='danger'>" + self.oneLink(rr, incomeLevel) + "</span>")
                moreExpensiveExists = True
        moreExpensive.append("</pre>")
        
        if moreExpensiveExists:
            out.extend(moreExpensive)        
        out.append("&nbsp;<br>&nbsp;<br>&nbsp;<br>")
        
        return out

    def stateFilteredSatRange(self, incomeLevel, stateAbbr, satMin, satMax=None):
        cacheKey = (incomeLevel, satMin, satMax)
        if cacheKey in self.cachedInfo:
            allRows = self.cachedInfo[cacheKey][:]
        else:
            allRows = self.generateOneSatRange(incomeLevel, satMin, satMax=None)
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
        
    
    def generateOneFile(self, incomeLevel=1, stateAbbr=''):
        if self.quiet is not True:
            print("Generating: ", stateAbbr, incomeLevel)
        outFilePath = self.outFilePath(incomeLevel, stateAbbr)                
        
        allRanges = []
        for satMin in range(700, 1500, 100):
            oneRangeStr = self.stateFilteredSatRange(incomeLevel, stateAbbr, satMin)
            allRanges.append(oneRangeStr)
        
        allAllStr = '\n'.join(allRanges)
        writeOut = self.template.format(dataGoesHere=allAllStr,
                                        stateAbbr=stateAbbr,
                                        stateName=stateNames[stateAbbr],
                                        incomeLevel=cc.incomeLevels[incomeLevel])
        with open(outFilePath, 'w', encoding='utf-8') as ofp:
            ofp.write(writeOut)
    
    
    def generateAll(self):
        for incomeLevel in range(1, 6):
            for stateAbbr in cc.stateList:
                self.generateOneFile(incomeLevel, stateAbbr)
            
if __name__ == '__main__':
    fg = FileGenerator()
    fg.generateAll()
    #fg.generateOneFile(2, None)
            
