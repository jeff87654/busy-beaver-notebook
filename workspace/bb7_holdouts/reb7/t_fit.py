import idle, sys, json, time
import fit7
def rows():
    U={}
    for p in ['../dl3_hits/out.tsv','../dl3_triage7/out.tsv','dl3_c.tsv','../../bb8_list/investigations/bb9_triage7_and_1RB1LA/new_dl3_out.tsv','../hits_triage7.tsv']:
        for l in open(p):
            f=l.rstrip('\n').split('\t')
            if len(f)>5 and f[0]!='machine' and f[0] not in U: U[f[0]]=f
    return U
U=rows()
m=sys.argv[1]
t=sys.argv[2] if len(sys.argv)>2 else U[m][4]
for tv,d in fit7.variants(t):
    t0=time.time()
    P=fit7.Prober(m,tv)
    try:
        R=fit7.fit_rules(P)
        print('OK',tv,'absorbed',d, '%.1fs'%(time.time()-t0))
        print(' F0',R['F0'],'A2',R['A2'],'B2',R['B2'],'excR2',R['excR2'],'smallD',R['smallD'][:5])
        for k in R['B']: print('  B%d'%k,R['B'][k],'small',R['smallB'][k][:6])
        print(' pat',R['Bpat'])
        print(' rand',fit7.check_random(P,R)[:3])
        for n in ([0] if P.Pempty else [0,1,2]):
            pat,best,res=fit7.fit_E(P,n,60)
            print(' E n=%d'%n,pat,best)
    except fit7.FitError as e:
        print('FAIL',tv,d,e,'%.1fs'%(time.time()-t0))
