"""ival.py MACHINE..: follow each machine from far_k + [0 1^n|1|R] (std and big policy, several k) with absolute
left tracking; print RSIGs (stage, |P|, c, z), the first non-K outcome, and the min visited cell.
usage: python ival.py M [M..] [--ks 17,29,41] [--policies std,big] [--n 41] [--S 120] [--marker BITS --gap G]"""
import sys, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF, rle
ap = argparse.ArgumentParser(); ap.add_argument('ms', nargs='+'); ap.add_argument('--ks', default='17')
ap.add_argument('--policies', default='std,big'); ap.add_argument('--n', type=int, default=41); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--S', type=int, default=120); ap.add_argument('--maxs', type=float, default=2e8); ap.add_argument('--nrs', type=int, default=4)
ap.add_argument('--marker', default=''); ap.add_argument('--gap', type=int, default=4); ap.add_argument('--v', action='store_true'); ap.add_argument('--ctrim', type=int, default=0)
a = ap.parse_args()
def run(M, k, pol):
    mk = a.marker + '0' * a.gap if a.marker else ''
    word = mk + far_of(k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    A = -len(mk); minlo = 0; rs = []; out = 'MAX'
    for st in range(a.S):
        kind, d = stage(M, word, int(a.maxs), pol, ctrim=a.ctrim)
        if d.get('LO') is not None: minlo = min(minlo, A + d['LO'])
        if kind != 'K':
            out = f'{kind}{d.get("slot", "")}@{st}'; break
        if a.v: print('   ', st, rle(d['toks'][:-2])[:160], 'far', len(d['far']), 'LO', A + d['LO'], flush=True)
        if mk and not (d['far'].startswith(a.marker + '0' * a.gap) and A + d['shift'] == -len(mk)) and A > -len(mk) - 10**9:
            if 'mk' not in locals(): pass
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3):
            rs.append((st, len(r[0]), r[1], r[2]))
            if len(rs) >= a.nrs: out = 'NRS'; break
        A += d['shift']; word = d['newword']
    return out, rs, minlo
def go():
    for M in a.ms:
        print(M)
        for k in map(int, a.ks.split(',')):
            for pol in a.policies.split(','):
                out, rs, lo = run(M, k, pol)
                print(f'  k={k} {pol}: {out} minlo={lo} RS=' + ' '.join(f'{s}:P{p}:c{c}:z{z}' for s, p, c, z in rs), flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
