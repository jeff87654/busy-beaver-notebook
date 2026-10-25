"""Literal verification of the n-list family rules of
   1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC
N(n_1..n_k) = 0^inf 1 ((10)^n_1 1) ... ((10)^n_k 1) G> 0^inf ; n_k = 2b+1 is the accumulator, n_2..n_{k-1} = 2d+1 digits,
n_1 = the far entry (odd: a digit; even: the 'top' entry of a rebuilt list).
Predicted next family configuration (the first G right-end event):
  R1   last digit n_{k-1} >= 3:              n_{k-1} -= 2, n_k += 4
  R23  nearest digit with units >= 2 is n_j (j < k-1), all later digits n=1 (zero):
                                             n_j -= 2, n_{j+1} = n_k + 2 (digit b+2), n_k = 1
  (n_1 even: its 'zero' is 0; n_1 odd: its zero is 1)
  EXH  all digits zero, n_1 = 1 (odd)  ->  rebuild: N(6, 1^(4b+m+6), 1) after parse failures (m = k-1 digits)
  HALT all digits zero, n_1 = 0        ->  halt in state J reading 0 with ones 2b + 2m + 3  (m = k-1 entries incl. n_1;
                                           = 2b + 2L + 5 with L = m-1 zero digits)
Every deviation is printed; the script exits nonzero on any mismatch.
"""
import subprocess, sys, random, itertools
FAM = './fam.exe'
def run(lines):
    inp = ''.join(l + '\n' for l in lines)
    out = subprocess.run([FAM], input=inp, capture_output=True, text=True).stdout.strip().split('\n')
    assert len(out) == len(lines), (len(out), len(lines))
    return out
def predict(ns):
    ns = list(ns); k = len(ns)
    b = ns[-1]
    digs = ns[:-1]
    def iszero(i):  # entry index i in digs
        return digs[i] == (0 if (i == 0 and digs[0] % 2 == 0) else 1)
    if not iszero(len(digs) - 1) and len(digs) - 1 > 0 or (len(digs) == 1 and digs[0] % 2 == 1 and digs[0] >= 3):
        d = digs[:]; d[-1] -= 2
        return ('EV', d + [b + 4])
    if len(digs) == 1 and digs[0] % 2 == 0 and digs[0] >= 2:
        d = digs[:]; d[-1] -= 2
        return ('EV', d + [b + 4])
    j = max((i for i in range(len(digs)) if not iszero(i)), default=None)
    if j is None:
        if digs[0] % 2 == 1:
            return ('REBUILD', [6] + [1] * (4 * ((b - 1) // 2) + len(digs) + 6) + [1])
        return ('HALT', 2 * ((b - 1) // 2) + 2 * len(digs) + 3)
    d = digs[:]; d[j] -= 2; d[j + 1] = b + 4 - 2  # digit b+2 -> units 2(b+2)+1 = 2b+5 ; b units n=2b+1 -> n+4
    d[j + 1] = b + 4
    return ('EV', d + [1])
def check(cases, maxsteps=10**9):
    lines = []
    for ns in cases:
        p = predict(ns)
        nev = 1 if p[0] == 'EV' else (2000 if p[0] == 'REBUILD' else 1)
        lines.append('%d %d %s' % (maxsteps, nev, ' '.join(map(str, ns))))
    outs = run(lines)
    bad = 0
    stats = {}
    for ns, o in zip(cases, outs):
        p = predict(ns)
        stats[p[0]] = stats.get(p[0], 0) + 1
        ok = False
        if p[0] == 'EV':
            toks = o.split()
            ok = toks[0] == 'EV' and list(map(int, toks[4:])) == p[1] and ';;' not in o
        elif p[0] == 'HALT':
            toks = o.split()
            ok = toks[0] == 'HALT' and toks[2] == 'J' and toks[3] == '0' and int(toks[4]) == p[1]
        else:
            evs = [e.strip() for e in o.split(';;')]
            fam = [e for e in evs if e.startswith('EV')]
            # first family event must be the predicted list, and only parse failures before it
            if fam:
                first = fam[0].split()
                ok = list(map(int, first[4:])) == p[1] and all(e.startswith('PARSEFAIL') for e in evs[:evs.index(fam[0])])
        if not ok:
            bad += 1
            if bad <= 15: print('MISMATCH', ns, 'pred', p if p[0] != 'REBUILD' else ('REBUILD', len(p[1])), 'got', o[:300])
    return bad, stats
if __name__ == '__main__':
    random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    cases = []
    # exhaustive small lists, odd entries (digits 0..3), b in a few values
    for m in range(1, 6):
        for ds in itertools.product(range(4), repeat=m):
            for b in (0, 1, 2, 5, 9):
                cases.append([2 * d + 1 for d in ds] + [2 * b + 1])
    # even first entry (0,2,4,6,8) with digits after it
    for m in range(0, 5):
        for top in (0, 2, 4, 6, 8):
            for ds in itertools.product(range(3), repeat=m):
                for b in (0, 1, 3, 8):
                    cases.append([top] + [2 * d + 1 for d in ds] + [2 * b + 1])
    # random longer lists, larger values
    for _ in range(3000):
        m = random.randint(1, 40)
        ds = [random.choice([0, 0, 0, 0, 1, 2, 3, 7, 20, 55]) for _ in range(m)]
        top = random.choice([None, 0, 2, 4, 6])
        ns = ([top] if top is not None else []) + [2 * d + 1 for d in ds] + [2 * random.choice([0, 1, 2, 3, 10, 40, 101, 333]) + 1]
        cases.append(ns)
    bad, stats = check(cases)
    print('rule checks:', len(cases), stats, 'bad', bad)
    sys.exit(1 if bad else 0)
