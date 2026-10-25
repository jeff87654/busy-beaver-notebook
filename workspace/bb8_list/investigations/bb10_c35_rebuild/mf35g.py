"""Generalised mini-follower (see mf35.py) for other 35-digit families: canonical state Q, K-moment tail suffix SUF,
accumulator offset E (r = 3b + E), start = the base machine's configuration at its first E0 read after the exhaustion
K(0^35; 0; b) built from a follow2-style template.  Uses stage35g.exe (server).

Family SIB (bb8-ab's F/H-relay sibling, template R,F,P=1,u=01,s=1,d=3d+1,b=3b+0,S=10101010, n = 35):
  K word = 1 (011)^36 (01)^(3b) 10101010, head on the blank right of it in state F;  SUF = 10101010, E = 0.
Family REC (the BB(8) record; for cross-checking against mf35.py): Q = G, SUF = 10101, E = 1.

  python mf35g.py FAMILY MACHINE [--stages N] [--maxs S] [-v]"""
from __future__ import annotations
import argparse, hashlib, os, subprocess, sys, tempfile, threading
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'bb8_champ35_1RB0RA_1LC0RH'))
from follow2 import Aff, Fail, jump
from numres import Num
from tmlit import Sim
import mf35

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
STAGE = str(HERE / 'stage35g.exe')

FAMILIES = {
    'REC': dict(base='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF', Q='G', SUF='10101', E=1,
                word=lambda b: '1' + '011' * 36 + '01' * (3 * b + 1) + '10101'),
    'SIB': dict(base='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC1RH_0LH0RF', Q='F', SUF='10101010', E=0,
                word=lambda b: '1' + '011' * 36 + '01' * (3 * b) + '10101010'),
}

_LOCAL = threading.local()
_CACHE = {}
_LOCK = threading.Lock()


def _server():
    sv = getattr(_LOCAL, 'sv', None)
    if sv is None or sv.poll() is not None:
        sv = subprocess.Popen([STAGE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                              creationflags=LOW)
        _LOCAL.sv = sv
    return sv


def run_stage(fam, machine, word, head, state, maxs, rcap=600):
    F = FAMILIES[fam]
    maxw = 4 * len(word) + 20000
    key = (fam, hashlib.sha1(word.encode()).digest(), head, state, maxs)
    sl = mf35._slots(machine)
    for mask, vals, out in _CACHE.get(key, ()):
        if all(sl[i] == v for i, v in zip(mask, vals)):
            return out
    sv = _server()
    q = 'ABCDEFGHIJ'.index(F['Q'])
    sv.stdin.write(f"{machine} {state} {head} {maxs} {maxw} {rcap} {q} {F['SUF']} {F['E']}\n{word}\n")
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    if not _:
        return line
    um = int(u, 16)
    mask = tuple(i for i in range(20) if um >> i & 1)
    with _LOCK:
        if len(_CACHE) > 60000:
            _CACHE.clear()
        _CACHE.setdefault(key, []).append((mask, tuple(sl[i] for i in mask), out))
    return out


_XC = {}


def xstart(fam, b):
    """the base machine's configuration at its first E0 read after K(0^35; 0; b): (word, head, state)"""
    if (fam, b) in _XC:
        return _XC[(fam, b)]
    F = FAMILIES[fam]
    w = F['word'](b)
    s = Sim.from_word(F['base'], '0000' + w + '0', 4 + len(w), F['Q'], size=1 << 20)
    while s.step():
        pass
    assert s.last == (4, 0), f'base halted at {s.last}, not E0'
    lo, hi = s.bounds()
    word = ''.join(map(str, s.tape[lo:hi + 1]))
    res = (word, s.pos - lo, 'E')
    _XC[(fam, b)] = res
    return res


def follow(fam, machine, stages=300, maxs=10_000_000, verbose=False, b0=6, M=2520, fixrep=None):
    F = FAMILIES[fam]
    E = F['E']
    LB = 3 * 6 + E
    word, head, state = xstart(fam, b0)
    hist, sigs = [], []
    for s in range(stages):
        out = run_stage(fam, machine, word, head, state, maxs)
        if not out:
            return 'FAIL', hist + ['no output']
        f = out.split()
        if f[0] == 'H':
            hist.append(f'H {f[2]}{f[3]} ones={f[4]}')
            return 'HALT', hist
        if f[0] in ('T', 'W'):
            hist.append(f[0])
            return {'T': 'TIME', 'W': 'WIDE'}[f[0]], hist
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            hist.append(f'J k={len(digits)} JUMPFAIL {ex}')
            return 'FAIL', hist
        vals = {p: (fixrep if fixrep and not v.exact else mf35.rep(v, M, LB)) for p, v in newp.items()}
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 2000:
            new[-1] = LB + ((new[-1] - LB) % M)
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        hist.append(f'J k={len(digits)} far={"junk" if far else "clean"} ev={info.get("event")} zeros={nz} '
                    f'r={",".join(str(v) for v in vals.values())}')
        if verbose:
            print(s, hist[-1], 'list:', mf35.rle(digits[:10]), '...', mf35.rle(digits[-10:]), flush=True)
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
        blocks = []
        for m in new:
            if blocks and blocks[-1][0] == m:
                blocks[-1][1] += 1
            else:
                blocks.append([m, 1])
        sigs.append((tuple(x[0] for x in blocks), tuple(x[1] for x in blocks) + (len(far),)))
        p = mf35.affine_period(sigs)
        if p:
            hist.append(f'LOOP p={p}')
            return 'LOOP', hist
    return 'MAXSTAGES', hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('family')
    ap.add_argument('machine')
    ap.add_argument('--stages', type=int, default=300)
    ap.add_argument('--maxs', type=int, default=10_000_000)
    ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    k, h = follow(a.family, a.machine, a.stages, a.maxs, a.v)
    print('RESULT', k, len(h), ' ; '.join(h))


if __name__ == '__main__':
    main()
