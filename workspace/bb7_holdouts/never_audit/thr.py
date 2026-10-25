"""thr.py JSONL OUT: where can the machine halt at all?  For each audited row: literal (exact) runs of the template step
from small configs [y, 0^k, A] (k = 0..8, A = 0..2k+8, y = 1,2) and from small exhaustions [X] (X = 0..40), each to the
next K-moment or halt (symsim exact = accelerated literal).  Reports the halting configs found and compares the
smallest A that halts per k with the smallest A the literal blank-tape run ever shows at a borrow over k zeros."""
import sys, json, os, idle_guard
from fam import *
from coding import VCoding, U10Coding, ChampCoding
CODINGS = {'V': VCoding(), 'U10': U10Coding(), 'U10s2': U10Coding(2), 'U110': U10Coding(1, 2), 'C1': ChampCoding()}
src, dst = sys.argv[1], sys.argv[2]
done = set()
try: done = set(json.loads(l)['machine'] for l in open(dst))
except Exception: pass
for l in open(src):
    R = json.loads(l)
    if R['machine'] in done or 'template' not in R: continue
    Q, side, TF, Z, cod = R['template']; Z = int(Z); TF = [] if TF == '-' else [int(x) for x in TF.split(',')]
    m = mirror(R['machine']) if side == 'L' else R['machine']; C = CODINGS[cod]
    halts = []
    def run(v):
        tp = C.encode(v, TF, Z, Q)
        verdict, st, fin, raw = run_sym(m, Q, tp, stopn=6, mg=720, budget=200000, tlimit=10, prove=True)
        return verdict
    for k in range(0, 9):
        for y in (1, 2):
            for A in range(0, 2 * k + 9):
                if run([y] + [0] * k + [A]) == 'HALT': halts.append(('B%d' % k, y, A))
    for X in range(0, 41):
        if run([X]) == 'HALT': halts.append(('E', X))
    minhalt = {}
    for h in halts:
        if h[0][0] == 'B': minhalt[int(h[0][1:])] = max(minhalt.get(int(h[0][1:]), -1), h[2])
    margins = {int(k): v for k, v in (R.get('margins') or {}).items()}
    unsafe = [k for k in margins if k in minhalt and margins[k] <= minhalt[k]]
    out = {'machine': R['machine'], 'halts': halts[:40], 'n_halts': len(halts), 'max_halting_A_by_k': minhalt,
           'literal_min_A_by_k': margins, 'unsafe': unsafe}
    with open(dst, 'a') as f: f.write(json.dumps(out) + '\n')
