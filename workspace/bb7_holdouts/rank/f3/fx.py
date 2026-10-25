"""fx.py: helper around sim.exe. Natural config for templates u=1,s=10 with K-moment b=0 fixed:
config (ds, a) <-> runs [d+1 for d in ds] + [a+1] + [LAST], head right of it.
nxt(mach, cfgs) -> list of results per cfg: ('K', ds, a, steps) | ('H', steps, ones) | ('T',) | ('W', step, runs-string)"""
import idle  # noqa
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, 'sim.exe')
MACH = {
    # name: (machine, orientation, state, tail runs after the a-run, gap)
    'A1': ('1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE', 'R', 'B', [1], 0),
    'A2': ('1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB', 'R', 'B', [1], 0),
    'B1': ('1RB0RD_0LC1LC_1LE1LD_1RE1LB_1RG1LF_---0LE_1RA1RG', 'L', 'C', [], 1),
    'C1': ('1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA', 'L', 'E', [6], 1),
}


def expand(s):
    out = []
    for x in s.split(','):
        if x == '...':
            out.append(None); continue
        if '^' in x:
            v, n = x.split('^'); out += [int(v)] * int(n)
        else:
            out.append(int(x))
    return out


def rle(r):
    o = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        o.append('%d' % r[i] + ('^%d' % (j - i) if j > i + 1 else '')); i = j
    return ','.join(o)


VCODE = {'C1'}   # v-coding: digit = run length (>=0), accumulator = run length


def runs_of(name, ds, a):
    M, O, Q, TL, G = MACH[name]
    if name in VCODE: return list(ds) + [a] + TL + [0] * G
    return [d + 1 for d in ds] + [a + 1] + TL + [0] * G


def sim(name, runs_list, maxs=10**8, maxev=1, filt=None):
    M, O, Q, TL, G = MACH[name]
    if filt is None: filt = '%d:%d' % (G, TL[-1] if TL else -1)
    inp = ''.join(('BLANK' if r == 'BLANK' else rle(r)) + chr(10) for r in runs_list)
    p = subprocess.run([SIM, M, O, Q, str(maxs), str(maxev), filt], input=inp, capture_output=True, text=True)
    res = []; cur = []
    for ln in p.stdout.splitlines():
        if ln == '.':
            res.append(cur); cur = []
        else:
            cur.append(ln.split())
    return res


def parse_ev(name, ev):
    """ev = ['E', step, gap, runs]; returns (ds, a) or None."""
    M, O, Q, TL, G = MACH[name]
    step, gap, r = int(ev[1]), int(ev[2]), expand(ev[3])
    nt = len(TL)
    if name in VCODE:
        if gap != G or None in r or len(r) < 1 + nt or (nt and r[-nt:] != TL): return None
        if nt: r = r[:-nt]
        ds = r[:-1]
        while ds and ds[0] == 0: ds = ds[1:]
        return ds, r[-1]
    if gap != G or None in r or len(r) < 1 + nt or (nt and r[-nt:] != TL) or min(r) < 1:
        return None
    if nt: r = r[:-nt]
    return [x - 1 for x in r[:-1]], r[-1] - 1


def nxt(name, cfgs, maxs=10**8):
    out = []
    rs = sim(name, [runs_of(name, ds, a) for ds, a in cfgs], maxs=maxs, maxev=1)
    for evs in rs:
        e = evs[0]
        if e[0] == 'E':
            pc = parse_ev(name, e)
            out.append(('K', pc[0], pc[1], int(e[1])) if pc else ('W', int(e[1]), e[2] + ':' + e[3]))
        elif e[0] == 'H':
            out.append(('H', int(e[1]), int(e[2])))
        else:
            out.append(('T',))
    return out


if __name__ == '__main__':
    name = sys.argv[1]
    for ln in sys.stdin:
        ln = ln.split()
        if not ln: continue
        ds = [] if ln[0] == '-' else expand(ln[0]); a = int(ln[1])
        r = nxt(name, [(ds, a)])[0]
        if r[0] == 'K': print(rle([x for x in ds]) or '-', a, '->', rle(r[1]) or '-', r[2], 'steps', r[3])
        else: print(rle(ds) or '-', a, '->', r)
