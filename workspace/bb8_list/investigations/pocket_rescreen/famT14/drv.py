import sys, subprocess, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle  # noqa
HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, 'sim.exe')
T1 = '1RB1LG_0RC0LB_1RD0RF_1LE---_1RF1RE_0LA0LG_0RH1LA_0RE1RC'
T2 = '1RB1LG_0RC0LB_1RD0RH_1LE1RC_1RF1RE_0LA0LG_0RD1LA_---0RE'
def lst(ds, a, b):
    return ''.join('1' * (2 * d) + '0' for d in ds) + '1' * (2 * a) + '0' + '1' * (2 * b) + '00'
def Q(m):
    return '1110' + '110' * m
def run(word, N, maxev, M=T1, q='B'):
    r = subprocess.run([SIM, M, '1', q, word, str(len(word)), str(N), 'B', str(maxev)], capture_output=True, text=True)
    return r.stdout.splitlines()
def rword(runs):
    return '0'.join('1' * r for r in runs) + '00'
def unr(s):
    o = []
    for t in s.split():
        c, _, k = t.partition('^'); o.append(c * (int(k) if k else 1))
    return ''.join(o)
def toruns(s):
    w = unr(s)
    assert w.endswith('000'), w[-10:]
    w = w[:-3]
    return [len(x) for x in w.split('0')]
def nxt(runs, N=10**8, M=T1, maxev=1):
    """run from K-config given as runs; return list of (step, runs) events, or ('H',step) etc."""
    out = []
    for L in run(rword(runs), N, maxev, M):
        p = L.split(None, 2)
        if p[0] == 'E': out.append((int(p[1]), toruns(p[2])))
        elif p[0] == 'H': out.append(('H', int(p[1])))
        elif p[0] == 'END' and len(p) == 2: out.append(('T', int(p[1])))
        elif p[0] == 'TAPE': out.append(('TAPE', int(p[1])))
    return out
def show(runs):
    s = []; i = 0
    while i < len(runs):
        j = i
        while j < len(runs) and runs[j] == runs[i]: j += 1
        r = runs[i]; t = ('M%d' % (r // 2)) if r % 2 else str(r // 2)
        s.append(t if j - i == 1 else '%s^%d' % (t, j - i)); i = j
    return ' '.join(s)
def parse_ds(s):
    r = []
    for t in s.split():
        rep = 1
        if '^' in t: t, rep = t.split('^'); rep = int(rep)
        v = 2 * int(t[1:]) + 1 if t[0] == 'M' else 2 * int(t)
        r += [v] * rep
    return r
def p1(s, a, b, M=T1, N=10**8):
    ev = nxt(parse_ds(s) + [2 * a, 2 * b], N=N, M=M, maxev=1)
    e = ev[0]
    if e[0] in ('H', 'T', 'TAPE'): return '%s %d' % e
    return show(e[1])
