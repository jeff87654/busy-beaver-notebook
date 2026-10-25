"""Shadow orbit driver v2: champion rules + macro clearing done modulo M (clearmod.py); every other situation is simulated
literally (fsnap.exe) until the next configuration with a stable tail.  The big digit block (1|)^K in Q is kept symbolic:
it is set to DIG digits before each literal run and the consumption is accumulated.
Usage: python shadow2.py START_SPEC MAXEVENTS"""
import sys, re, subprocess, os
from fam import FAM, expand_list, cl, spec_of_word, M as MACHINE
from trace import word as spec_word
import clearmod as CM
from clearmod import red, big, C, iterate, M, CNT
HERE = os.path.dirname(os.path.abspath(__file__))
DIG = 300
BLOCK = re.compile(r'\^(\d+)')
def stable(h, tail):
    return (h == 3 and tail == [1]) or (h == 8 and len(tail) >= 2 and tail[-2:] == [1, 1] and all(x == 6 for x in tail[:-2]))
def word_of_cfg(c):
    q = spec_word(c['Q']) + '0' * c['g'] if c['Q'] else ''
    w = q + ''.join('10' * t + '1' for t in c['toks']) + '10' * c['r'] + '1' * c['h']
    for x in c['tail']: w += '00' + '1' * x
    return w
def literal(w, maxsteps=3 * 10**9):
    spec = spec_of_word(w)
    p = subprocess.Popen([os.path.join(HERE, os.environ.get('FSNAP_EXE', 'fsnap.exe')), MACHINE, spec, str(maxsteps), '3', '1000000000'], stdout=subprocess.PIPE, text=True,
                         env=dict(os.environ, FSZ=str(1 << 27)))
    out = None
    for line in p.stdout:
        if line.startswith('HALT') or line.startswith('EDGE'):
            out = dict(halt=line.strip()); break
        m = FAM.match(line)
        if m:
            c = dict(step=int(m.group(1)), Q=m.group(3).strip(), g=int(m.group(4)), toks=expand_list(m.group(5)), r=int(m.group(6)), h=int(m.group(7)), tail=expand_list(m.group(8)))
            if stable(c['h'], c['tail']): out = c; break
    p.kill(); p.wait()
    return out
def _blk(Q):
    lo = int(os.environ.get('BLO', DIG - 60)); hi = int(os.environ.get('BHI', DIG + 60))
    ms = [m for m in BLOCK.finditer(Q) if lo <= int(m.group(1)) <= hi]
    return ms[0] if len(ms) == 1 else (None if not ms else 'MULTI')
def blockcount(Q):
    if os.environ.get('NORESET'): return None
    m = _blk(Q)
    if m == 'MULTI': raise SystemExit('multiple block candidates in ' + Q)
    return int(m.group(1)) if m else None
def set_block(Q, n):
    m = _blk(Q)
    return Q[:m.start()] + f'^{n}' + Q[m.end():]
def red_other(Q):  # reduce big counts (tokens inside Q); the block (count near DIG) is < M and untouched
    return re.sub(r'\^(\d+)', lambda m: '^' + str(red(int(m.group(1)))), Q)
def cnt_of(x):  # number of borrows from token x (x>=3), exact or big
    q = (x - x % 3) // 3
    return q if not big(x) else CM.OFF * M + q % CNT
def digit(y):
    assert y % 3 == 2
    return (2 * y + 2) // 3 if not big(y) else CM.OFF * M + ((2 * y + 2) // 3) % CNT
def step_rules(t, r):
    """apply standard rules until an event; returns (t, r, nsteps, reason)"""
    n = 0
    while True:
        a = t[-1] if t else None
        if a is None: return t, r, n, 'empty'
        if a >= 3:
            N = cnt_of(a) if a % 3 else ((a // 3) if not big(a) else CM.OFF * M + (a // 3) % CNT)
            r = C(1, r, N); t = t[:-1] + [a % 3]; n += 1; continue
        if a == 1:
            i = len(t) - 2
            while i >= 0 and t[i] == 1: i -= 1
            if i < 0 or t[i] in (0, 2): return t, r, n, 'fail1'
            x = t[i]; k = len(t) - 1 - i
            if r % 3 == 2:
                q = cnt_of(x)
                r = iterate(lambda y: C(k, 2, digit(y)), r, q)
                t = t[:i] + [x % 3] + [1] * k; n += 1; continue
            t = t[:]; t[i] = x - 3 if not big(x) else red(x - 3 + M); t[i + 1] = red(2 * r + 3); r = 2; n += 1; continue
        if a == 0:
            if len(t) >= 2 and t[-2] >= 4:
                t = t[:-1]; t[-1] = t[-1] - 4 if not big(t[-1]) else red(t[-1] - 4 + M); t.append(red(2 * r + 3)); r = 2; n += 1; continue
            return t, r, n, 'fail0'
        return t, r, n, 'a2'
def show(c, extra=''):
    if 'halt' in c: return c['halt']
    q = c['Q']; q = q if len(q) < 200 else q[:90] + ' ... ' + q[-100:]
    return f"Q[{q}] g={c['g']} {cl(c['toks'])} r={c['r']} h={c['h']} tail{cl(c['tail'])}{extra}"
def normalize(c):
    c['toks'] = [red(x) for x in c['toks']]; c['r'] = red(c['r']); c['Q'] = red_other(c['Q']); return c
def main():
    start = sys.argv[1]; maxev = int(sys.argv[2])
    if start.startswith('CFG:'):   # CFG:Q;g;t1,t2,...;r;h;tail1,tail2,...
        q, g, ts, r, h, tl = start[4:].split(';')
        c = dict(Q=q, g=int(g), toks=[int(x) for x in ts.split(',') if x], r=int(r), h=int(h), tail=[int(x) for x in tl.split(',') if x])
    else:
        c = literal(spec_word(start))
    consumed = 0
    print('start ->', show(c)); sys.stdout.flush()
    nev = 0
    while nev < maxev and c and 'halt' not in c:
        c = normalize(c)
        if stable(c['h'], c['tail']):
            t, r, n, why = step_rules(c['toks'], c['r'])
            c = dict(c, toks=t, r=r)
        else: n, why = 0, 'unstable'
        bc = blockcount(c['Q'])
        if bc is not None and not os.environ.get('NORESET'): c['Q'] = set_block(c['Q'], DIG)
        before = show(c, f'  [{n} rule steps, {why}]')
        c2 = literal(word_of_cfg(c))
        nev += 1
        used = None
        if c2 and 'halt' not in c2:
            bc2 = blockcount(c2['Q'])
            base = DIG if not os.environ.get('NORESET') else bc
            used = (base - bc2) if (bc is not None and bc2 is not None) else ('BLOCK GONE' if bc is not None else None)
            if isinstance(used, int): consumed += used
        if os.environ.get('COMPACT'):
            k = int(os.environ['COMPACT'])
            after = (f"..{c2['Q'][-k:]} | {cl(c2['toks'])} r={c2['r']} h={c2['h']} t{cl(c2['tail'])}" if c2 and 'halt' not in c2 else str(c2))
            print(f"EV{nev} [{n},{why}] ..{c['Q'][-k:]} | {cl(c['toks'])} r={c['r']} h={c['h']} t{cl(c['tail'])}\n      -> {after}  used {used} tot {consumed}")
        else:
            print(f'EV{nev}: {before}\n   -> {show(c2) if c2 else "NONE"}   digits used: {used} (total {consumed})')
        sys.stdout.flush()
        c = c2
    print('END', show(c) if c else None)

if __name__ == '__main__':
    import threading
    sys.setrecursionlimit(1000000)
    threading.stack_size(1 << 27)
    th = threading.Thread(target=main); th.start(); th.join()
