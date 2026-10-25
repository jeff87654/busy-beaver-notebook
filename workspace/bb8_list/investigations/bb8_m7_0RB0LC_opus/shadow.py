"""Shadow orbit driver: standard champion rules applied symbolically (numbers kept exact if small, else reduced mod M
into [M,2M)); every other situation is simulated literally (fsnap.exe) until the next configuration with a stable tail.
Usage: python shadow.py START_SPEC MAXEVENTS [M]"""
import sys, re, subprocess, os, json
from fam import FAM, expand_list, cl, spec_of_word, M as MACHINE
from trace import word as spec_word
HERE = os.path.dirname(os.path.abspath(__file__))
Mod = 504
LIMIT = 2 * Mod
def red(v): return v if v < LIMIT else Mod + (v % Mod)
def red_spec(Q):
    return re.sub(r'\^(\d+)', lambda m: '^' + str(red(int(m.group(1)))), Q)
def stable(h, tail):
    return (h == 3 and tail == [1]) or (h == 8 and len(tail) >= 2 and tail[-2:] == [1, 1] and all(x == 6 for x in tail[:-2]))
def word_of_cfg(c):
    q = spec_word(c['Q']) + '0' * c['g'] if c['Q'] else ''
    w = q + ''.join('10' * t + '1' for t in c['toks']) + '10' * c['r'] + '1' * c['h']
    for x in c['tail']: w += '00' + '1' * x
    return w
def literal(w, maxsteps=3 * 10**9, maxcfg=200000):
    spec = spec_of_word(w)
    p = subprocess.Popen([os.path.join(HERE, 'fsnap.exe'), MACHINE, spec, str(maxsteps), '3', '1000000000'], stdout=subprocess.PIPE, text=True,
                         env=dict(os.environ, FSZ=str(1 << 27)))
    out = None
    for line in p.stdout:
        if line.startswith('HALT'):
            out = dict(halt=line.strip()); break
        m = FAM.match(line)
        if m:
            c = dict(step=int(m.group(1)), Q=m.group(3).strip(), g=int(m.group(4)), toks=expand_list(m.group(5)), r=int(m.group(6)), h=int(m.group(7)), tail=expand_list(m.group(8)))
            if stable(c['h'], c['tail']):
                out = c; break
        elif line.startswith('RAW'):
            pass
    p.kill(); p.wait()
    return out
def rules(c):
    t, r = c['toks'], c['r']
    if not t: return None
    a = t[-1]
    if a >= 3:
        mf = a % 3; N = (a - mf) // 3
        rn = pow(2, N) * (r + 4) - 4 if N < 4000 else None
        return 'R1x%d' % N, t[:-1] + [mf], red(rn)
    if a == 1:
        i = len(t) - 2
        while i >= 0 and t[i] == 1: i -= 1
        if i >= 0 and t[i] >= 3:
            u = t[:]; u[i] = red(u[i] - 3) if u[i] - 3 >= 3 or u[i] < LIMIT else u[i] - 3; u[i + 1] = red(2 * r + 3)
            return 'R23', u, 2
        return None
    if a == 0 and len(t) >= 2 and t[-2] >= 4:
        u = t[:-1]; u[-1] = u[-1] - 4; u.append(red(2 * r + 3))
        return 'R0', u, 2
    return None
def show(c):
    if 'halt' in c: return c['halt']
    q = c['Q']; q = q if len(q) < 160 else q[:70] + ' ... ' + q[-80:]
    return f"Q[{q}] g={c['g']} {cl(c['toks'])} r={c['r']} h={c['h']} tail{cl(c['tail'])}"
if __name__ == '__main__':
    start = sys.argv[1]; maxev = int(sys.argv[2])
    if len(sys.argv) > 3: Mod = int(sys.argv[3]); LIMIT = 2 * Mod
    w = spec_word(start)
    c = literal(w)
    print('start ->', show(c)); sys.stdout.flush()
    nev = 0; nrules = 0
    while nev < maxev and c and 'halt' not in c:
        c['toks'] = [red(x) for x in c['toks']]; c['r'] = red(c['r']); c['Q'] = red_spec(c['Q'])
        rr = rules(c) if stable(c['h'], c['tail']) else None
        if rr:
            name, toks, r = rr; c = dict(c, toks=toks, r=r); nrules += 1
            continue
        before = show(c)
        c2 = literal(word_of_cfg(c))
        nev += 1
        print(f'EV{nev} ({nrules} rule steps before): {before}\n      -> {show(c2) if c2 else "NONE (step limit)"}'); sys.stdout.flush()
        nrules = 0
        c = c2
    print('END', show(c) if c else None)
