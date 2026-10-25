# predict.py runs/<file> : checks EVERY post-ESC CL view and the HALT against the abstract endgame model (key 31, P' = K mod 5),
# using the policy accumulators R printed on the J lines.  Also checks rin=2 (b = 0 at every CL) when the lines carry it, and
# the halting ones formula  ones = sum_{tokens left of the cleared suffix}(x+1) + 2(k+1) + 6R + 4t + 8.
import sys, re
def ex(v):
    o = []
    for i, x in enumerate(v):
        if '*' in x and i < len(v) - 1: a, b = x.split('*'); o += [a] * int(b)
        else: o.append(x)
    return o
def T(R): return str(6 * R + 7)
def model(res, K, RE, Rs):
    """expected list of (tail tokens, view count) for the CL views after the ESC; Rs = policy R's of those CLs (in order)."""
    out = []; it = iter(Rs)
    if res == 'b':
        out.append((['3', T(RE)], K)); R = next(it); out.append((['0', T(R)], K)); next(it)
    elif res == 0:
        z = (3 * K - 30) // 5; C = 6 * RE + (3 * K + 45) // 5; out.append((['2', '1', str(C), '7'], z)); R = next(it)
        for c in range(C - 3, -1, -3): out.append((['2', '1', str(c), T(R)], z)); R = next(it)
    elif res == 1:
        z = (3 * K - 33) // 5; out.append((['2', '3', str(6 * RE + 8), '2', 'z2', str(z + 7)], z)); Ra = next(it)
        out.append((['2', '3', str(6 * RE + 7), str(6 * Ra + 10)], z - 1, 2)); Rb = next(it)
        out.append((['2', '0', T(Rb)], z)); next(it)
    elif res == 2:
        z = (3 * K - 21) // 5; C = (3 * K + 9) // 5; out.append((['2', '4', str(6 * RE + 1), str(C), '7'], z)); R = next(it)
        for c in range(C - 3, -1, -3): out.append((['2', '4', str(6 * RE + 1), str(c), T(R)], z)); R = next(it)
    elif res == 3:
        z = (3 * K - 34) // 5; C = (3 * K - 9) // 5; pre = ['2', '3', str(6 * RE + 6), '2', 'z2']
        out.append((pre + [str(C), '7'], z)); R = next(it)
        for c in range(C - 3, -1, -3): out.append((pre + [str(c), T(R)], z)); R = next(it)
        out.append((['2', '3', str(6 * RE + 4), str(6 * R + 10)], z, 2)); Ry = next(it)
        out.append((['2', '0', T(Ry)], z + 1)); next(it)
    else:
        z = (3 * K - 37) // 5; C = (3 * K - 12) // 5; pre = ['2', '2', str(6 * RE + 7), 'z2', '0', '2', 'z2']
        out.append((pre + [str(C), '7'], z)); R = next(it)
        for c in range(C - 3, -1, -3): out.append((pre + [str(c), T(R)], z)); R = next(it)
        C2 = 6 * R + 6 * RE + 15; out.append((['2', '1', str(C2), '7'], z - 1)); R = next(it)
        for c in range(C2 - 3, -1, -3): out.append((['2', '1', str(c), T(R)], z - 1)); R = next(it)
    return [o if len(o) == 3 else o + (1,) for o in out]   # (tail, view count, number of nonzero digits cleared)
nbad = nrun = nviews = 0; byres = {}
for r in open(sys.argv[1]).read().split('== ')[1:]:
    L = r.strip().split('\n'); lab = L[0]; J = [l for l in L if l.startswith('J')]; end = L[-1]; nrun += 1
    vw = [ex(l.split('|', 1)[1].split()) for l in J]; Rs = [int(re.search(r'R=(\d+)', l).group(1)) for l in J]
    rins = [re.search(r'rin=(\d+)', l) for l in J]
    if any(m and m.group(1) != '2' for m in rins): print('RIN!=2', lab); nbad += 1
    ie = next(i for i, v in enumerate(vw) if v[-2] == '7' and v[-3] in ('2', '6'))
    K = int(vw[ie][-1].split('*')[1]); RE = Rs[ie]; res = K % 5 if vw[ie][-3] == '2' else 'b'; pre = vw[ie][:-5] if res != 'b' else vw[ie][:-3]
    try: exp = model(res, K, RE, Rs[ie + 1:] + [None] * 5)
    except StopIteration: exp = None
    kin = [int(re.search(r' k=(\d+)', l).group(1)) for l in J[ie + 1:]]
    got = [(v[len(pre):-1], int(v[-1].split('*')[1]), kk - int(v[-1].split('*')[1]) + 1) for v, kk in zip(vw[ie + 1:], kin)]
    ok = exp is not None and got == exp[:len(got)] and len(got) == len(exp) and end.startswith('HALT') and all(v[:len(pre)] == pre for v in vw[ie + 1:])
    if ok:
        l = J[-1]; t = int(re.search(r't=(\d+)', l).group(1)); k = int(re.search(r' k=(\d+)', l).group(1)); R = Rs[-1]
        toks = [int(x.split('*')[0]) * 0 + int(x.split('*')[0]) for x in vw[-1] if not x.startswith('z')]
        flat = []
        for x in l.split('|', 1)[1].split():
            if x.startswith('z'): continue
            a, _, b = x.partition('*'); flat += [int(a)] * (int(b) if b else 1)
        pred = sum(x + 1 for x in flat[:len(flat) - (k + 1)]) + 2 * (k + 1) + 6 * R + 4 * t + 8
        H = int(re.search(r'ones (\d+)', end).group(1)); ok &= pred == H
    nviews += len(got); byres[res] = byres.get(res, 0) + 1
    if not ok:
        nbad += 1; print('MISMATCH', lab, 'K', K, 'res', res)
        for a, b in zip(got, exp or []):
            if a != b: print('   got', a, '\n   exp', b); break
print('runs', nrun, 'views checked', nviews, 'by res', byres, 'mismatches', nbad)
