"""eval2.py TAG 'rule' ...: misses / pass rates of python rules over pf7 columns (r = row dict, ints converted).
Sets: hits2416 (graded by dlscan2 1M/20k in hits_dl2_1M.tsv), calset (23 cal + champion + 14 h14), s2000 (random),
ext (2,885 dlscan2-graded 9-10 state machines from bb8_list investigations, ext_graded.tsv)."""
from analyze import *
import os, sys
IMP = ('CHAMPION', 'R4-SOME', 'HALT?', 'HALT-SOME', 'CHECK')
dl = load_dl2('hits_dl2_1M.tsv')
tag = sys.argv[1]
pf = load_pf(f'pf_hits2416_{tag}.tsv'); rnd = load_pf(f'pf_s2000_{tag}.tsv'); cal = load_pf(f'pf_calset_{tag}.tsv')
ext = load_pf(f'pf_ext_{tag}.tsv') if os.path.exists(f'pf_ext_{tag}.tsv') else {}
eg = {l.split('\t')[0]: l.split('\t')[1] for l in open('ext_graded.tsv')}
graded = [m for m, (g, t) in dl.items() if g != '-']
imp = [m for m, (g, t) in dl.items() if g in IMP]
def conv(r): return {k: (int(v) if v.lstrip('-').isdigit() else v) for k, v in r.items()}
P = {m: conv(r) for m, r in pf.items()}; C = {m: conv(r) for m, r in cal.items()}; R = [conv(r) for r in rnd.values()]
E = {m: conv(r) for m, r in ext.items()}
for rule in sys.argv[2:]:
    f = eval('lambda r: ' + rule)
    ok = lambda r: r['halted'] >= 0 or f(r)
    mi = sum(not ok(P[m]) for m in imp); mg = sum(not ok(P[m]) for m in graded); mc = sum(not ok(C[m]) for m in C)
    ei = sum(not ok(E[m]) for m in E if eg[m] in IMP); en = sum(not ok(E[m]) for m in E if eg[m] not in IMP)
    nei = sum(eg[m] in IMP for m in E)
    print(f'{rule:70s} hits miss imp {mi}/{len(imp)} all {mg}/{len(graded)} | cal {mc}/{len(C)} | ext imp {ei}/{nei} nob {en}/{len(E)-nei} | random pass {sum(ok(r) for r in R)/len(R):.3f}')
