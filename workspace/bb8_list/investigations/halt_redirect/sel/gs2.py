"""gs2.py: continue the lazy enumeration from a list of (partial) machines through a chain of tests.
usage: python gs2.py IN.tsv OUT.tsv CHAIN   (CHAIN = name of a test chain defined below; IN rows: machine<TAB>...)"""
import sys, collections
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import gsearch, stageu
from gsearch import OPTS, E0OPTS, mk, run
CHAINS = {
    # stage 0 (real start), first-period transient, then the exhaustion stage (recorded, branched)
    'EXH': [('T3', 6, 'K: 6^16 8 1^102 | a=1 r=2'),
            ('T4', '6^16 5 0 1^101 1 19', 'K: 6^14 4 5 37 1^108 | a=1 r=1'),
            ('T2', '1 41 0 1^19 1 19', None)],
    'T2only': [('T2', '1 41 0 1^19 1 19', None)],
}
def slots_of(m):
    p = m.split('_')
    return {'E0': p[4][:3], 'I0': p[8][:3], 'I1': p[8][3:], 'J0': p[9][:3], 'J1': p[9][3:]}
def search_from(sl0, tests, log):
    results = collections.Counter()
    def rec(sl, ti):
        if ti == len(tests): return
        name, inp, exp = tests[ti]
        out, used = run(sl, tests[ti]); f = out.split()
        if f[0] == 'H':
            slot = f[2] + f[3]
            if slot in sl and sl[slot] == '---':
                results[(name, 'HALT@' + slot)] += 1
                log.write(f'{mk(sl)}\t{name}\tHALT@{slot}\n'); log.flush()
                for v in (E0OPTS if slot == 'E0' else OPTS):
                    s2 = dict(sl); s2[slot] = v; rec(s2, ti)
                return
            results[(name, 'HALT*' + slot)] += 1; log.write(f'{mk(sl)}\t{name}\tHALT*{slot}\n'); return
        if f[0] in ('T', 'W'):
            results[(name, f[0])] += 1; log.write(f'{mk(sl)}\t{name}\t{f[0]}\n'); return
        key = stageu.fmt(out).rsplit(' step=', 1)[0]
        if exp is not None:
            if key != exp:
                results[(name, 'DIFF')] += 1; log.write(f'{mk(sl)}\t{name}\tDIFF {key}\n'); return
            if ti == len(tests) - 1:
                results[(name, 'SAME')] += 1; log.write(f'{mk(sl)}\t{name}\tSAME\n'); return
            rec(sl, ti + 1)
        else:
            results[(name, key)] += 1; log.write(f'{mk(sl)}\t{name}\t{key}\n'); log.flush()
            if ti < len(tests) - 1: rec(sl, ti + 1)
    rec(sl0, 0)
    return results
if __name__ == '__main__':
    src, out, chain = sys.argv[1], sys.argv[2], sys.argv[3]
    tot = collections.Counter()
    with open(out, 'w') as log:
        for l in open(src):
            m = l.split('\t')[0].strip()
            if not m: continue
            tot += search_from(slots_of(m), CHAINS[chain], log)
    for k, v in sorted(tot.items(), key=lambda x: -x[1])[:80]:
        print(v, k)
