"""farfol.py: follow M from far_k + [0 1^n | 1 | R]; at every round-start signature report the far region's
leading D2 count (kD2), the rest of the far string, the prefix P, counter c (class mod 14) and depth z.
lib use: track(M, k, n, R, policy, nrs, maxst) -> dict(rs=[(st, kD2, restlen, P, c, z)], end=kind, slot, minlo)"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from ilib import stage, rsig, far_of, word_of, rle, SUF
import mf35

def fark(far):
    k = 0
    while far.startswith('10101', 5 * k): k += 1
    return k, far[5 * k:]

def track(M, k=29, n=29, R=19, policy='std', nrs=5, maxst=400, maxs=2 * 10**8, bigk=1, verbose=False, cmin=6, start=None):
    word = start if start else far_of(k) + word_of([0] + [1] * n + [1, R]) + SUF
    A = 0; out = {'rs': [], 'end': 'MAX', 'slot': None, 'minlo': 0, 'st': 0}
    lastrs = -10
    for st in range(maxst):
        kind, d = stage(M, word, maxs, policy, bigk)
        if d.get('LO') is not None: out['minlo'] = min(out['minlo'], A + d['LO'])
        out['st'] = st
        if kind != 'K':
            out['end'] = kind; out['slot'] = d.get('slot'); return out
        r = rsig(d['toks'])
        if verbose:
            kd, rest = fark(d['far'])
            print(f'  {st}: far kD2={kd} rest={len(rest)}b toks={rle(d["toks"][:-2])[:150]} | a={d["toks"][-2]} r={d["toks"][-1]}', flush=True)
        if r and r[1] >= cmin and st - lastrs > 3 and st > 0:
            kd, rest = fark(d['far'])
            out['rs'].append((st, kd, len(rest), r[0], r[1], r[2], rest[:60]))
            lastrs = st
            if len(out['rs']) >= nrs:
                out['end'] = 'RS'; return out
        A += d['shift']; word = d['newword']
    return out

def fmt(o):
    s = ' '.join(f'[st{st} k{kd} t{rl} P{len(P)} c{c}/{c%14} z{z}]' for st, kd, rl, P, c, z, _ in o['rs'])
    return f'{o["end"]} {o["slot"] or ""} st={o["st"]} minlo={o["minlo"]} {s}'

if __name__ == '__main__':
    M = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 29; n = int(sys.argv[3]) if len(sys.argv) > 3 else 29
    pol = sys.argv[4] if len(sys.argv) > 4 else 'std'; nrs = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    v = len(sys.argv) > 6
    threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
    t = threading.Thread(target=lambda: print(fmt(track(M, k, n, policy=pol, nrs=nrs, verbose=v)))); t.start(); t.join()
