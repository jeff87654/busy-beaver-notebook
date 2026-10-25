from dfam import *
import sys
pre=[(),(1,),(2,),(3,),(4,),(1,1),(2,2)]
for c in range(0,17):
    row=[]
    for p in pre:
        r=nextD(p+(c,) if c>0 else p,1,3000000) if True else None
        if r is None: row.append("TO")
        else:
            t,d,y=r
            row.append("H" if d=="HALT" else "%s|%d"%("".join(map(str,d)) if all(x<10 for x in d) else d,y))
    print(c,row)
