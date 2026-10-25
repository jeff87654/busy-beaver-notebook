"""ana2.py: classify all henum leaves.  For each h_*.tsv (+ .eng from engchk.py):
 blank H (>=1e5 steps) -> 'late halter'; blank X/C -> runaway/cycler; blank T + engine intact -> exhaustion-chain analysis;
 blank T + engine modified -> 'modified'.
Chain (engine intact): next-E parity after a rebuild (ds; a): F1/F2 Phi = a + sum(ds) mod 2; F3: 1 if len(ds) >= 2 else a mod 2
 (last borrow B1 sets an odd accumulator; D keeps parity).  Nondeterministic over A values of one parity in the grid.
 Output per leaf: maxR = max #rebuilds before a halting E over both start parities ('inf-class' if a cycle reaches H)."""
import sys, os, glob, collections
from bcfg import BASES
AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]
def expand(s):
    out = []
    for x in s.split(','):
        if not x: continue
        if '^' in x: v, n = x.split('^'); out += [int(v)] * int(n)
        else: out.append(int(x))
    return out
def po(x):
    if x.startswith('K:'):
        p = x.split(':'); ds, a, b = p[1].split(';'); return ('K', expand(ds), int(a))
    return (x[0],)
def nextpar(fam, ds, a, x=None):
    if x is not None: return (x * a + sum(ds)) % 2
    if fam == 'F3': return 1 if len(ds) >= 2 else a % 2
    return (a + sum(ds)) % 2
def chain(fam, cols, x=None):
    em = {A: po(c) for A, c in zip(AS, cols)}
    tr = {}
    for p in (0, 1):
        outs = [em[A] for A in AS if A % 2 == p]
        kinds = set(o[0] for o in outs)
        nx = set(); halt = False; unk = False
        for o in outs:
            if o[0] == 'H': halt = True
            elif o[0] == 'K': nx.add(nextpar(fam, o[1], o[2], x))
            else: unk = True
        tr[p] = (halt, nx, unk)
    # longest path to a halt (in rebuild counts) from p
    best = {}
    def dfs(p, stack):
        halt, nx, unk = tr[p]; r = 0 if halt else None; cyc = False; u = unk
        for q in nx:
            if q in stack:
                if reach_halt(q): cyc = True
                continue
            sub, c2, u2 = dfs(q, stack | {q}); cyc |= c2; u |= u2
            if sub is not None: r = max(r if r is not None else -1, sub + 1)
        return r, cyc, u
    def reach_halt(q, seen=None):
        seen = seen or set()
        if tr[q][0]: return True
        seen.add(q); return any(reach_halt(x, seen) for x in tr[q][1] if x not in seen)
    res = {}
    for p in (0, 1): res[p] = dfs(p, {p})
    return tr, res
if __name__ == '__main__':
    files = sorted(glob.glob('h_*.tsv'))
    stat = collections.Counter(); late = []; cand = []; seen = set(); nonk = []; noinv = []
    for fn in files:
        tag = os.path.basename(fn)[2]; fam = BASES[tag][3]
        eng = {}; inv = {}
        if os.path.exists(fn + '.inv'):
            for l in open(fn + '.inv'):
                p = l.rstrip().split(chr(9))
                if len(p) == 5: inv[p[0]] = (int(p[1]), int(p[2]), int(p[3]), float(p[4]))
        if os.path.exists(fn + '.eng'):
            for l in open(fn + '.eng'): m, ok, mis = l.split('\t'); eng[m] = ok == '1'
        for l in open(fn):
            f = l.rstrip('\n').split('\t')
            if l.startswith('#') or len(f) < 3: continue
            m = f[1]
            if m in seen: stat['dup'] += 1; continue
            seen.add(m); st = f[2][0]
            if st == 'H':
                stat['late halter (>=1e5 steps, blank)'] += 1; s = f[2].split(':'); late.append((int(s[1]), int(s[2]), tag, f[0], m)); continue
            if st != 'T': stat['blank ' + st] += 1; continue
            if m not in eng: stat['T no eng'] += 1; continue
            x = None; pre = 'intact: '
            if not eng[m]:
                iv = inv.get(m)
                if iv is None: stat['modified, no inv data'] += 1; continue
                nK, o0, o1, kf = iv
                if kf < 0.5: stat['modified, non-K engine'] += 1; nonk.append((tag, f[0], m)); continue
                if o1 == nK: x = 1
                elif o0 == nK: x = 0
                else: stat['modified K-like, no mod-2 invariant'] += 1; noinv.append((tag, f[0], m, f[3:])); continue
                pre = f'modified K-like (Phi_{x}): '
            tr, res = chain(fam, f[3:], x)
            mx = max((r[0] for r in res.values() if r[0] is not None), default=None)
            cyc = any(r[1] for r in res.values())
            key = pre + ('never halts at E' if mx is None and not cyc else f'max rebuilds before halt = {mx}' + (' + CYCLE-to-halt (class)' if cyc else ''))
            stat[key] += 1
            if cyc or (mx is not None and mx >= 1): cand.append((tag, f[0], m, mx, cyc, {p: (tr[p][0], sorted(tr[p][1]), tr[p][2]) for p in tr}))
    for k, v in sorted(stat.items()): print(f'{v:8d}  {k}')
    print('--- late blank halters (top 30 by steps)')
    for x in sorted(late, reverse=True)[:30]: print(*x)
    print('--- intact chains with >=1 rebuild before a halt, or class cycles:', len(cand))
    for x in cand: print(*x, sep='\t')
    open('nonk_leaves.txt', 'w').write(''.join(m + chr(9) + tag + chr(9) + t + chr(10) for tag, t, m in nonk))
    open('noinv_leaves.txt', 'w').write(''.join(m + chr(9) + tag + chr(9) + t + chr(9) + chr(9).join(c) + chr(10) for tag, t, m, c in noinv))
