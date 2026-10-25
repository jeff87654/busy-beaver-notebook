from analyze import *
import sys
dl = load_dl2('hits_dl2_1M.tsv')
feats = ['R6','R12','R24','R36','R312','R324','T6','T12','T24','T36','T312','T324']
for steps in sys.argv[1:]:
    pf = load_pf(f'pf_hits2416_{steps}.tsv'); rnd = load_pf(f'pf_s2000_{steps}.tsv'); cal = load_pf(f'pf_calset_{steps}.tsv')
    print('steps', steps)
    graded = [m for m,(g,t) in dl.items() if g != '-']
    imp = [m for m,(g,t) in dl.items() if g in ('CHAMPION','R4-SOME','HALT?','HALT-SOME','CHECK')]
    for f in feats:
        for thr in (1,2,3):
            miss_imp = sum(int(pf[m][f]) < thr for m in imp)
            miss_gr = sum(int(pf[m][f]) < thr for m in graded)
            miss_cal = sum(int(cal[m][f]) < thr for m in cal)
            pr = sum(int(r[f]) >= thr for r in rnd.values()) / len(rnd)
            print(f'  {f:5s}>={thr}: miss imp {miss_imp}/{len(imp)} graded {miss_gr}/{len(graded)} cal {miss_cal}/{len(cal)}  random pass {pr:.3f}')
