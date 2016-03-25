'''
Find all colleges where the cost is lower for higher incomes.
'''

import collegeCosts as cc

def findScrewy():
    rr = cc.readFile()
    r2 = cc.filterRows(rr, satMin=0, satMax=2000)

    for r in r2:
        cPrev = r.cost(1)
        for il in range(2, 6):
            cNow = r.cost(il)
            if cNow is not None and cPrev is not None and cNow < cPrev:
                print(r.unitid, r.shortName(), il, "$", cNow, "<", cPrev)
            cPrev = cNow

if __name__ == '__main__':
    findScrewy()
