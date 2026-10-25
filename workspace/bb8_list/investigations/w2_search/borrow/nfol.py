"""nfol.py: follower (copy of halt_redirect/mf/ord_run.follow) for n1-based machines with up to 16 states, using gstage.exe.
Start from the real start (b0) or from a constructed config: --start "0 1^5 1 19" (digits farthest first, then a, r)
and optional --far BITS / --fark K (far = (10101)^K + n1's fixed 44-bit tail).
usage: python nfol.py MACHINE [--start ..] [--fark K] [--policy std|big|shrink] [--stages 80] [--maxs 2e8] [--b0 6]"""
import idle  # noqa: F401  (Idle priority)

import sys, os, subprocess, argparse, threading, ctypes
HERE = os.path.dirname(os.path.abspath(__file__))
MF = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf'
sys.path.insert(0, MF)
import mf35g, mf35
from follow2 import Aff, Fail, jump
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
GSTAGE = os.path.join(HERE, 'gstage.exe')
FAR_TAIL = '10110101010101010010000010111100100100100100'
_LOCAL = threading.local()

def _server():
    sv = getattr(_LOCAL, 'sv', None)
    if sv is None or sv.poll() is not None:
        sv = subprocess.Popen([GSTAGE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                              creationflags=0x40)
        _LOCAL.sv = sv
    return sv

def run_stage(machine, word, head, state, maxs, Q='G', SUF='1010', E=1, rcap=600, maxw=None):
    maxw = maxw or (4 * len(word) + 20000)
    sv = _server()
    q = 'ABCDEFGHIJKLMNOP'.index(Q)
    sv.stdin.write(f"{machine} {state} {head} {maxs} {maxw} {rcap} {q} {SUF} {E}\n{word}\n")
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    return (out, int(u, 16)) if _ else (line, 0)

def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)

def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v

def follow(M, b0=6, policy='std', stages=80, maxs=2 * 10**8, bigk=1, log=print, start=None, far='', hist=None):
    """returns (result, history); history = list of (stage, kind, tokens(list), far, info)"""
    F = mf35g.FAMILIES['GH']; E = F['E']; LB = 19; MM = 2520
    if start is not None:
        word = far + mf35.word_of_tokens(start) + F['SUF']; head, state = len(word), F['Q']
    else:
        word, head, state = mf35g.xstart('GH', b0)
    H = hist if hist is not None else []
    for s in range(stages):
        out, used = run_stage(M, word, head, state, maxs)
        if not out:
            log(f'{s} FAIL no output'); return 'FAIL', H
        f = out.split()
        if f[0] == 'H':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]} U={used:x}'); H.append((s, 'HALT', f, '', used)); return 'HALT', H
        if f[0] in ('T', 'W', 'X'):
            log(f'{s} {f[0]} {out[:100]}'); H.append((s, f[0], f, '', used)); return f[0], H
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        log(f'{s} K: {rle(digits)} | a={toks[1]} r={toks[0]}' + (f' far={far}' if far else '') + f' U={used:x}')
        H.append((s, 'K', digits + [toks[1], toks[0]], far, used))
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError, KeyError, ZeroDivisionError) as ex:
            log(f'{s} JUMPFAIL {ex}'); H.append((s, 'JUMPFAIL', str(ex), far, used)); return 'FAIL', H
        vals = {}
        for p, v in newp.items():
            if v.exact:
                vals[p] = mf35.rep(v, MM, LB)
            else:
                base = mf35.rep(v, MM, LB)
                vals[p] = base if policy == 'std' else base + MM * bigk
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 2000 and policy == 'std':
            new[-1] = LB + ((new[-1] - LB) % MM)
        if policy == 'shrink':
            for i in range(len(new) - 1):
                if new[i] > 2539:
                    new[i] = LB + ((new[i] - LB) % MM)
            if new[-1] > 2000:
                new[-1] = LB + ((new[-1] - LB) % MM) + MM * bigk
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz} lv={info.get("level")} -> {rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        H.append((s, 'J', new, far, info.get('event')))
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
    return 'MAXSTAGES', H

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('--start', default=None); ap.add_argument('--policy', default='std')
    ap.add_argument('--stages', type=int, default=80); ap.add_argument('--maxs', type=float, default=2e8)
    ap.add_argument('--b0', type=int, default=6); ap.add_argument('--bigk', type=int, default=1)
    ap.add_argument('--fark', type=int, default=None); ap.add_argument('--far', default='')
    ap.add_argument('--log', default=None)
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None
    def log(s):
        print(s, flush=True)
        if lf: lf.write(s + '\n'); lf.flush()
    far = a.far or ('10101' * a.fark + FAR_TAIL if a.fark is not None else '')
    sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
    res = []
    t = threading.Thread(target=lambda: res.append(follow(a.machine, a.b0, a.policy, a.stages, int(a.maxs), a.bigk, log,
                                                         expand(a.start) if a.start else None, far)))
    t.start(); t.join()
    log(f'RESULT {res[0][0] if res else "CRASH"}')
