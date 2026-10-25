"""rules.py: rule-level models (natural coding) for A1/A2/B1/C1 + random literal check.
step(name, ds, a) -> ('K', ds, a, visible) | ('H',)   visible=False for silent rules (absorb)."""
import idle  # noqa
import random, sys
import fx


def E_A1(A, extra):
    # [;A] rebuild of A1; extra = number of additional 2s (E2: +1, E1: -1)
    m, r = divmod(A, 4)
    if r == 0: return ('H',)
    if r == 1: n, tail, a = 3 * m, [1], 2
    elif r == 2: n, tail, a = 3 * m + 1, [], 2
    else: n, tail, a = 3 * m, [1], 14
    n += extra
    if n < 0:
        # degenerate E1(1): [3,1] minus a 2 -> [2]
        if (A, extra) == (3, -1): return ('K', [2], 14, True)
        return ('?',)
    return ('K', [3] + [2] * n + tail, a, True)


RULES = {}


def step_A1(ds, a):
    if not ds: return E_A1(a, 0)
    if ds[-1] >= 1: return ('K', ds[:-1] + [ds[-1] - 1], 3 * a + 5, True)
    if len(ds) == 1: return E_A1(a + 2, -1)
    if ds[-2] == 0:
        if len(ds) == 2: return E_A1(a, +1)
        return ('K', ds[:-3], a + ds[-3] + 2, False)
    return ('K', ds[:-2] + [ds[-2] - 1, 3 * a + 6], 2, True)


RULES['A1'] = step_A1
RULES['A2'] = step_A1


def run_rules(name, ds, a, nvis):
    seq = []
    st = RULES[name]
    for _ in range(10000):
        r = st(ds, a)
        if r[0] != 'K':
            seq.append(r); return seq
        ds, a = r[1], r[2]
        if r[3]:
            seq.append((tuple(ds), a))
            if len(seq) >= nvis: return seq
    return seq


def check(name, ds, a, nvis=6, maxs=3 * 10**7):
    seq = run_rules(name, list(ds), a, nvis)
    if seq and seq[-1][0] == '?': return 'skip', seq
    # literal: collect b=0 events
    big = max([a] + [max(s[0]) if s[0] != 'H' and s[0] else 0 for s in seq if s[0] != 'H'] + [x[1] for x in seq if x[0] != 'H'])
    if big > 3000: seq = [x for x in seq]  # still fine; literal events printing is capped
    evs = fx.sim(name, [fx.runs_of(name, ds, a)], maxs=maxs, maxev=4000)[0]
    lit = []
    for e in evs:
        if e[0] == 'E':
            pc = fx.parse_ev(name, e)
            if pc: lit.append((tuple(pc[0]), pc[1]))
        elif e[0] == 'H':
            lit.append(('H',))
        else:
            lit.append((e[0],))
    # subsequence check
    i = 0
    for x in lit:
        if i < len(seq) and x == seq[i]: i += 1
    if i == len(seq): return 'ok', seq
    # inconclusive if literal ran out of budget before reaching
    if lit and lit[-1][0] in ('T', 'X', 'TAPE'): return 'budget', (seq, i, lit[-3:])
    return 'MISS', (seq, i, lit[:12])


def step_B1(ds, a):
    if not ds: return ('H',) if a % 2 == 0 else ('K', [2], 3 * a + 4, True)
    if ds[-1] >= 1: return ('K', ds[:-1] + [ds[-1] - 1], 3 * a + 4, True)
    if len(ds) == 1: return ('H',) if a % 2 == 0 else ('K', [2, 3 * a + 5], 1, True)
    if ds[-2] == 0:
        if len(ds) == 2: return ('H',)
        return ('K', ds[:-3], a + ds[-3] + 2, False)
    return ('K', ds[:-2] + [ds[-2] - 1, 3 * a + 5], 1, True)


def strip0(ds):
    i = 0
    while i < len(ds) and ds[i] == 0: i += 1
    return ds[i:]


def step_C1(ds, r):
    ds = strip0(ds)
    if not ds:
        if r % 3 == 1: return ('H',)
        if r == 0: return ('K', [], 4, True)
        m, q = divmod(r, 3)
        if q == 2: return ('K', [1, 0, 2] + [6] * m, 6, True)
        return ('K', [4] + [6] * (m - 1), 6, True)
    if ds[-1] >= 1: return ('K', strip0(ds[:-1] + [ds[-1] - 1]), 2 * r + 2, True)
    k = 0
    while ds[-1 - k] == 0: k += 1
    R = 2 * r + 2 - 6 * k
    if R < 1: return ('?',)
    return ('K', strip0(ds[:-(k + 1)] + [ds[-(k + 1)] - 1, R] + [6] * (k - 1)), 6, True)


RULES['B1'] = step_B1
RULES['C1'] = step_C1


if __name__ == '__main__':
    name, seed, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    maxd = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    random.seed(seed)
    cnt = {}
    for t in range(N):
        n = random.randint(0, 7)
        ds = []
        for _ in range(n):
            ds.append(0 if random.random() < 0.45 else random.randint(1, maxd))
        a = random.randint(0, 9)
        res, info = check(name, ds, a)
        cnt[res] = cnt.get(res, 0) + 1
        if res not in ('ok',):
            print(res, ds, a, info)
    print(name, 'seed', seed, cnt)
