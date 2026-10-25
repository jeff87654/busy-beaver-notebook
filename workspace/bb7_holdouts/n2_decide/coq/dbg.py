from rules_def import *
import sys
nm=sys.argv[1]; vals=dict(kv.split('=') for kv in sys.argv[2:])
S,Tg=RULES[nm]
for v,k in vals.items():
    S=engine.subst(S,v,(),int(k)); Tg=engine.subst(Tg,v,(),int(k))
pl.drive(nm,S,Tg,maxev=2000)
