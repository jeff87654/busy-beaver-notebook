# val.py: helper. probe(machine, Q, side, list of 'X left|right' strings) -> list of (kind, steps, rawleft, state, rawright)
import sys, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2\sim.exe'
def expand(w):
    o = []
    for g in re.finditer(r'\(([01]+)\)\^(\d+)|([01])\^(\d+)|([01])', w):
        if g.group(1): o.append(g.group(1) * int(g.group(2)))
        elif g.group(3): o.append(g.group(3) * int(g.group(4)))
        else: o.append(g.group(5))
    return ''.join(o)
def probe(m, Q, side, cfgs, N=10**10):
    inp = '\n'.join(cfgs) + '\n'
    out = subprocess.run([EXE, m, '1', 'probe', Q, side, str(N)], input=inp, capture_output=True, text=True).stdout.strip().split('\n')
    res = []
    for ln in out:
        if ln.startswith('S '):
            mm = re.match(r'S (\d+) (\w) \| (.*) <\w> (.*)$', ln)
            res.append(('S', int(mm.group(1)), expand(mm.group(3)), mm.group(2), expand(mm.group(4))))
        elif ln.startswith('H'): res.append(('H', int(ln.split()[1]), None, None, None))
        else: res.append(('T', 0, None, None, None))
    return res
def check(m, Q, side, cases, fmt, parse, rule, N=10**10):
    """cases: list of param tuples; fmt(params)->cfg string; parse(left,right)->params or None; rule(params)->expected params or 'H'"""
    res = probe(m, Q, side, [fmt(c) for c in cases], N)
    bad = 0
    for c, r in zip(cases, res):
        exp = rule(c)
        got = 'H' if r[0] == 'H' else (parse(r[2], r[4]) if r[0] == 'S' else 'T')
        if got != exp:
            bad += 1
            if bad <= 8: print('MISMATCH', c, 'exp', exp, 'got', got, (r[2][:60], r[4][:60]) if r[0]=='S' else '')
    print(f'{m}: {len(cases)} cases, {bad} mismatches')
    return bad
def bounce_round(m, Q, R, A, B, pre='0', maxev=200, N=10**10, mid='', da=2, canjump=None, nojump=False):
    """From config Q at left edge with right word R (raw), run events until next config pre A^x B^y T with y>=2,
    accelerating any pre A^x B^y T (y>=2) as x+=2(y-1), y=1. Returns (x,y,T) of the first y>=2 event after the start, or ('H',) / ('T',)."""
    pat = re.compile('^' + pre + '((?:' + A + ')*)' + mid + '((?:' + B + ')*)(.*?)0*$')
    first = True
    for ev in range(maxev):
        g = pat.match(R)
        if g: x, y, T = len(g.group(1))//len(A), len(g.group(2))//len(B), g.group(3)
        if g and y >= 2 and (canjump is None or canjump(x, y, T)):
            if not first: return (x, y, T)
            if not nojump: R = pre + A*(x+da*(y-1)) + mid + B + T
        first = False
        r = probe(m, Q, 'L', [f'{Q} |{R}'], N)[0]
        if r[0] != 'S': return (r[0],)
        if r[2].strip('0'): return ('L?',)
        R = r[4]
    return ('maxev',)
def short(t):
    import subprocess
    return t if len(t) < 70 else t[:30] + '..(' + str(len(t)) + ')..' + t[-30:]
def chain(m, Q, R, A, B, pre, rounds, mid='', da=2):
    """run bounce_round repeatedly; yields (x,y,tail)"""
    out = []
    for _ in range(rounds):
        r = bounce_round(m, Q, R, A, B, pre=pre, mid=mid, da=da, maxev=2000)
        out.append(r)
        if len(r) < 3: break
        x, y, T = r
        R = pre + A*x + mid + B*y + T
    return out
