"""ilib.py: follower stage with absolute left-end tracking (igstage.exe).  stage() returns (kind, d) where d is a dict:
  K: toks (digits farthest-first + [a, r]), far, newword, ev, nz, new, LO, MW, shift (abs offset of the new word's
     first cell relative to the old word's first cell)
  H: slot, steps, ones, LO, MW;   T/W/JF: LO, MW (if known)
Absolute coordinate convention: cell 0 = the first cell of the START word (its leftmost 1)."""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, os, subprocess, threading, ctypes
HERE = os.path.dirname(os.path.abspath(__file__))
MF = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf'
sys.path.insert(0, MF)
import mf35
from follow2 import Aff, Fail, jump
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
EXE = os.path.join(HERE, 'fgstage.exe')
FAR_TAIL = '10110101010101010010000010111100100100100100'
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
MM = 2520; LB = 19; SUF = '1010'
_L = threading.local()

def _server():
    sv = getattr(_L, 'sv', None)
    if sv is None or sv.poll() is not None:
        sv = subprocess.Popen([EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=0x40)
        _L.sv = sv
    return sv

def raw(M, word, maxs, head=None, state='G', rcap=600, ll=-(1 << 60), lvs=0):
    head = len(word) if head is None else head
    sv = _server()
    sv.stdin.write(f"{M} {state} {head} {maxs} {4 * len(word) + 20000} {rcap} 6 {SUF} 1 {ll} {lvs}\n{word}\n"); sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    x = None; g = None
    if ' | G ' in out:
        out, _, gs = out.rpartition(' | G ')
        gl = gs.split(); g = (int(gl[0]), gl[1:])
    if ' | X ' in out:
        out, _, xs = out.rpartition(' | X ')
        x = [int(v) for v in xs.split()]
    return out, x, g, int(u, 16) if u else 0

def D(m): return '10' * m + '1'
def word_of(toks): return ''.join(D(m) for m in toks)
def far_of(k): return '10101' * k + FAR_TAIL
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            a, c = t.split('^'); v += [int(a)] * int(c)
        else:
            v.append(int(t))
    return v
def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)

def trim_counter(new, ct):
    """shrink every run '2 5 1^m' with m > ct to m' = ct + (m - ct) mod 5040 ... no: m' = (m mod 42) + 42*(ct // 42)
    (keeps the counter class mod 42; used to follow a big-policy round to its end quickly)"""
    out = list(new); i = 0
    while i + 2 < len(out) - 2:
        if out[i] == 2 and out[i + 1] == 5:
            j = i + 2
            while j < len(out) - 2 and out[j] == 1: j += 1
            m = j - i - 2
            if m > ct:
                m2 = (m % 42) + 42 * (ct // 42)
                out = out[:i + 2] + [1] * m2 + out[j:]
                j = i + 2 + m2
            i = j
        else:
            i += 1
    return out

def stage(M, word, maxs=2 * 10**7, policy='std', bigk=1, ll=-(1 << 60), lvs=0, ctrim=0, head=None, state='G'):
    out, x, g, used = raw(M, word, maxs, head=head, state=state, ll=ll, lvs=lvs)
    f = out.split()
    d = {'LO': x[0] if x else None, 'MW': x[1] if x else None, 'U': used, 'G': g}
    if not f:
        return 'FAIL', d
    if f[0] == 'H':
        d.update(slot=f[2] + f[3], steps=int(f[1]), ones=int(f[4])); return 'H', d
    if f[0] in ('T', 'W', 'X', 'L'):
        return f[0], d
    parts = out.split('|')
    toks = [int(v) for v in parts[1].split()]
    far = parts[2].strip() if len(parts) > 2 else ''
    L1, P = x[2], x[3]
    digits = toks[2:][::-1]
    ent = []
    for m in digits:
        if ent and ent[-1][1] == m: ent[-1][2] += 1
        else: ent.append(['D', m, 1])
    left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
    d.update(toks=digits + [toks[1], toks[0]], far=far, shift=(L1 if far else P + 1))
    try:
        items, newp, info = jump(left, [], {}, 1)
    except (Fail, AssertionError, RuntimeError, RecursionError, KeyError, ZeroDivisionError) as ex:
        d['err'] = str(ex)[:60]; return 'JF', d
    vals = {}
    for p, v in newp.items():
        base = mf35.rep(v, MM, LB)
        vals[p] = base if (v.exact or policy == 'std') else base + MM * bigk
    new = []
    for e in items:
        m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
        c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
        new += [m] * c
    if len(new) >= 2 and new[-1] > 2000 and policy == 'std':
        new[-1] = LB + ((new[-1] - LB) % MM)
    if policy == 'shrink':
        for i in range(len(new) - 1):
            if new[i] > 2539: new[i] = LB + ((new[i] - LB) % MM)
        if new[-1] > 2000: new[-1] = LB + ((new[-1] - LB) % MM) + MM * bigk
    if ctrim:
        new = trim_counter(new, ctrim)
    nz = 0
    for m in new[:-2][::-1]:
        if m != 1: break
        nz += 1
    d.update(newword=far + mf35.word_of_tokens(new) + SUF, ev=info.get('event'), nz=nz, new=new)
    return 'K', d

def rsig(toks):
    """round-start signature: digits 'P 2 5 1^c 0^3 9 1^z' (or '... 0^3 3 1^z' after a J) -> (P, c, z) else None"""
    d = toks[:-2]
    for i in range(len(d) - 2):
        if d[i] == 2 and d[i + 1] == 5:
            j = i + 2; c = 0
            while j < len(d) and d[j] == 1: c += 1; j += 1
            if c >= 6 and d[j:j + 3] == [0, 0, 0] and j + 3 < len(d) and d[j + 3] == 9 and all(v == 1 for v in d[j + 4:]):
                return (tuple(d[:i]), c, len(d) - j - 4)
    return None

def follow(M, word, stages=100, policy='std', maxs=2 * 10**7, log=print, bigk=1):
    """follow with absolute tracking; returns list of records (stage, kind, d, abs_word_start)"""
    A = 0; H = []
    for s in range(stages):
        kind, d = stage(M, word, maxs, policy, bigk)
        lo = None if d.get('LO') is None else A + d['LO']
        mw = None if d.get('MW') is None or d['MW'] >= 10**17 else A + d['MW']
        if kind != 'K':
            log(f'{s} {kind} {d.get("slot", "")} LO={lo} MW={mw}'); H.append((s, kind, d, A)); return kind, H
        far = d['far']
        rs = rsig(d['toks'])
        log(f'{s} K: {rle(d["toks"][:-2])} | a={d["toks"][-2]} r={d["toks"][-1]} far={len(far)}b'
            f'{"[" + far[:40] + "..]" if far else ""} LO={lo} MW={mw} start={A}->{A + d["shift"]}'
            + (f' RSIG P={list(rs[0])} c={rs[1]} z={rs[2]}' if rs else ''))
        H.append((s, kind, d, A))
        A += d['shift']; word = d['newword']
    return 'MAX', H

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('--start', default='0 1^41 1 19'); ap.add_argument('--fark', type=int, default=17)
    ap.add_argument('--marker', default=''); ap.add_argument('--policy', default='std'); ap.add_argument('--stages', type=int, default=80)
    ap.add_argument('--maxs', type=float, default=2e7); ap.add_argument('--real', type=int, default=None)
    a = ap.parse_args()
    if a.real is not None:
        import mf35g
        w, h, q = mf35g.xstart('GH', a.real)
        raise SystemExit('real start needs head/state E; use nfol for that')
    word = a.marker + far_of(a.fark) + mf35.word_of_tokens(expand(a.start)) + SUF
    sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
    t = threading.Thread(target=lambda: print('RESULT', follow(a.machine, word, a.stages, a.policy, int(a.maxs))[0])); t.start(); t.join()

def real_start(b0=6):
    """(word, head, state) of n1's first stage from the real start (mf35g.xstart('GH', b0))"""
    import mf35g
    return mf35g.xstart('GH', b0)
