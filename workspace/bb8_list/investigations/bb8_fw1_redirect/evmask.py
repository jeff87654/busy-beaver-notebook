"""evmask.py: slots read by each K-level event of the base (E, D, B1, B2, B3) from constructed configs (pure Python)."""
import idle, re
from bcfg import *
def parse(w, t, B0):
    P, S, u, s = t['P'], t['S'], t['u'], t['s']
    if not (w.startswith(P) and w.endswith(S)) or len(w) < len(P)+len(S): return None
    body = w[len(P):len(w)-len(S)]
    parts = body.split(s) if s else None
    runs = [len(x) for x in parts]
    if any(set(x) - {'1'} for x in parts): return None
    if len(runs) < 2: return None
    b = runs[-1]
    if b < t['beB'] or (b - t['beB']) % t['alB'] or (b - t['beB']) // t['alB'] != B0: return None
    for r in runs[:-1]:
        if r < t['be'] or (r - t['be']) % t['al']: return None
    v = [(r - t['be']) // t['al'] for r in runs[:-1]]
    return (v[:-1], v[-1])
def run(M, t, B0, ds, a, maxs=200000):
    mir = t['o'] == 'L'
    tr = {}
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-': d = 1 if x[1] == 'R' else -1; tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    w = kl.word(t, ds, a, B0); tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos, q, Q = len(w), 0, ord(t['q']) - 65; q = Q; used = set()
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones); ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse(ww, t, B0)
                if k is not None: return ('K', k, used)
        if (q, c) not in tr: return ('H', (chr(65+q), c), used)
        used.add(chr(65+q) + str(c)); W, d, nq = tr[(q, c)]; tape[pos] = W; pos += d; q = nq
    return ('T', None, used)
for tag in BASES:
    M, tt, B0, fam = BASES[tag]; t = T(tag); res = {}
    for name, ds, a in [('E', [], 6), ('Eo', [], 7), ('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 6), ('B3', [2, 0, 0, 0], 7)]:
        k, r, used = run(M, t, B0, ds, a); res[name] = (k, r, used)
    allD = set().union(*(res[n][2] for n in ('D', 'B1', 'B2', 'B3')))
    Eonly = sorted((res['E'][2] | res['Eo'][2]) - allD)
    print(tag, fam, 'E-only:', ' '.join(Eonly) or '-', '| B-only:', ' '.join(sorted(set().union(*(res[n][2] for n in ('B1','B2','B3'))) - res['D'][2] - res['E'][2] - res['Eo'][2])) or '-',
          '| E:', res['E'][0], res['E'][1] and (len(res['E'][1][0]), res['E'][1][1]), 'Eo:', res['Eo'][0], '| D:', res['D'][1], 'B1:', res['B1'][1], flush=True)
