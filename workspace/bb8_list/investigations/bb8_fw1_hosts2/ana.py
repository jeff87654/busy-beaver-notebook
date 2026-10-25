import idle, sys, os, collections
from fam import BASES, dec
def load(nm,mode):
    labs=[l.rstrip('\n').split('\t') for l in open('bat/%s.rarelab'%nm)]
    V=[]
    for l in open('out/%s.m%s'%(nm,mode)):
        if l.startswith('#'): continue
        m,o=l.rstrip('\n').split('\t'); V.append((m,o.split('|')))
    return labs,V
def kind(o,f):
    if o=='=': return '='
    if o[0]=='H': return 'H'
    if o[0] in 'TX': return o[0]
    return 'M'
if __name__=='__main__':
    for nm in sys.argv[2:] or BASES:
        f=BASES[nm][3]
        labs,V=load(nm,sys.argv[1])
        cnt=collections.Counter()
        for m,outs in V:
            ks=''.join(kind(o,f) for o in outs)
            cls='ALLHALT' if set(ks)<= {'=','H'} else ('NEWCFG' if 'M' in ks else 'TX')
            cnt[cls]+=1
        print(nm,dict(cnt))
