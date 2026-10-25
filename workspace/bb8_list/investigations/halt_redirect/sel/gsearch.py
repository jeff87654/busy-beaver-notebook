"""gsearch.py: lazy (TNF-style) enumeration of the I/J gadget (and E0 in {0LI,0RI,1LI,1RI}) of the GH family, branching
only on slots actually read, through a sequence of literal stage tests.
Each test: (name, tokens-or-xstart, expected-output-or-None).  A machine passes a test with an expectation iff the stage
output equals it; a test without expectation records the outcome.  Halts at an undefined I/J slot are branched (40 ways)
for tests with expectations; for the final test they are recorded as HALT@slot (and also branched if --branch-final).
usage: python gsearch.py OUT.tsv"""
import sys, itertools, collections
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35, stageu
MAXS = 200_000
BASE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_{E0}0LC_0RG1LD_1RH1LG_1LC0RG_{I0}{I1}_{J0}{J1}'
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHIJ']
E0OPTS = ['0LI', '0RI', '1LI', '1RI']
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1','J0','J1']
def mk(sl):
    return BASE.format(**sl)
def run(sl, test):
    name, inp, exp = test
    m = mk(sl)
    if isinstance(inp, int):
        w, h, s = mf35g.xstart('GH', inp); out, used = stageu.run_word(m, w, h, s, MAXS)
    else:
        out, used = stageu.stage(m, inp, maxs=MAXS)
    return out, used
def search(tests, log, branch_final=False):
    results = collections.Counter(); nrun = [0]
    def rec(sl, ti):
        if ti == len(tests):
            return
        name, inp, exp = tests[ti]
        out, used = run(sl, tests[ti]); nrun[0] += 1
        f = out.split()
        if f[0] == 'H':
            slot = f[2] + f[3]
            if slot in sl and sl[slot] == '---':
                if ti == len(tests) - 1:
                    results[(name, 'HALT@' + slot)] += 1
                    log.write(f'{mk(sl)}\t{name}\tHALT@{slot}\n'); log.flush()
                    if not branch_final: return
                for v in (E0OPTS if slot == 'E0' else OPTS):
                    s2 = dict(sl); s2[slot] = v; rec(s2, ti)
                return
            # halt at a defined slot?? impossible; or at a base slot: record
            results[(name, 'HALT*' + slot)] += 1; return
        if f[0] in ('T', 'W'):
            results[(name, f[0])] += 1
            if ti == len(tests) - 1: log.write(f'{mk(sl)}\t{name}\t{f[0]}\n')
            return
        key = stageu.fmt(out).rsplit(' step=', 1)[0]
        if exp is not None:
            if key != exp:
                results[(name, 'DIFF')] += 1
                if ti == len(tests) - 1: log.write(f'{mk(sl)}\t{name}\tDIFF {key}\n')
                return
            if ti == len(tests) - 1:
                results[(name, 'SAME')] += 1; log.write(f'{mk(sl)}\t{name}\tSAME\n'); return
            rec(sl, ti + 1)
        else:
            results[(name, key)] += 1
            log.write(f'{mk(sl)}\t{name}\t{key}\n'); log.flush()
            if ti < len(tests) - 1: rec(sl, ti + 1)
    rec({'E0': '---', 'I0': '---', 'I1': '---', 'J0': '---', 'J1': '---'}, 0)
    return results, nrun[0]
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--phase', default='T1')
    ap.add_argument('--branch-final', action='store_true')
    a = ap.parse_args()
    T1 = ('T1', '6^4 1 41 0 1^19 1 19', None)
    T1c = ('T1c', '6^3 0 1^20 1 19', None)
    tests = {'T1': [T1], 'T1c': [T1c]}[a.phase]
    with open(a.out, 'w') as log:
        res, n = search(tests, log, a.branch_final)
    print('stage runs', n)
    for k, v in sorted(res.items(), key=lambda x: -x[1])[:60]:
        print(v, k)
