import idle, sys, os, collections
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import fit7
HERE=os.path.dirname(os.path.abspath(__file__))
nof=[l.split('\t')[0] for l in open(os.path.join(HERE,'summary1.tsv')) if '\tNOFIT' in l]
T=collections.OrderedDict()
for l in open(os.path.join(HERE,'t_all.tsv')):
    f=l.rstrip('\n').split('\t')
    if f[1]!='NONE': T.setdefault(f[0],[]).append(f[1])
T['1RB0LF_0RC0LG_1LD1RE_0RC---_1LA0RB_1RG0RD_1LE0RF']=['L,A,P=11,u=110,s=0,d=1d+0,b=1b+0,S=11']
combos=[(S,b,d) for S in ['0','-','1','01','00','10','11'] for b in ['2b+1','2b+0','1b+0'] for d in ['1d+0','2d+0']]
good=collections.Counter()
out=open(os.path.join(HERE,'sweep.tsv'),'a')
for m in nof:
    bases=[]
    for t in T.get(m,[])[:3]:
        O,Q=t.split(',')[:2]; kv=dict(x.split('=',1) for x in t.split(',')[2:])
        b=(O,Q,kv['P'],kv['u'],kv['s'])
        if b not in bases: bases.append(b)
    found=None
    order=sorted(combos,key=lambda c:-good[c])
    for (O,Q,P,u,s) in bases:
        for (S,bb,dd) in order:
            tm='%s,%s,P=%s,u=%s,s=%s,d=%s,b=%s,S=%s'%(O,Q,P,u,s,dd,bb,S)
            try:
                R=fit7.fit_rules(fit7.Prober(m,tm)); found=tm; good[(S,bb,dd)]+=1; break
            except Exception as e:
                pass
        if found: break
    out.write('%s\t%s\n'%(m,found or 'NONE')); out.flush(); print(m,found,flush=True)
