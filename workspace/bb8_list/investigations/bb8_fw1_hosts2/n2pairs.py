import idle, os, re, sys, collections
os.environ['EVPAIRS']='1'
from fam import run
M='1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA'
r=run(M,'R','A',['B'],int(sys.argv[1]) if len(sys.argv)>1 else 3*10**8,200000,'-')[0]
ev=[]; prev=None
for x in r:
    p=x.split()
    if p[0]!='M': print('end',x[:40]); break
    st=int(p[1]); pairs=set(re.findall('...',p[2].split(':')[1])); bits=p[3]
    if prev is not None: ev.append((prev[0],st,len(prev[1]),len(bits),pairs,prev[1],bits))
    prev=(st,bits)
print('events',len(ev),'last step',ev[-1][1],'last len',ev[-1][3])
# a 'rebuild' event: tape grows by > 8 cells in one event
eng=set(); rare=collections.defaultdict(set); nre=0
for e in ev:
    if e[3]-e[2]>8: nre+=1; rare['grow>8']|=e[4]
    else: eng|=e[4]
print('engine pairs',len(eng),sorted(eng)); print('rebuild events',nre)
for k,v in rare.items(): print(k,'rare-only:',sorted(v-eng))
import pickle; pickle.dump(ev,open('n2ev.pkl','wb'))
