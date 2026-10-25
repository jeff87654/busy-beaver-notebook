"""myfol.py: own stage follower for c1 (independent of mf35g/follow2/ord_run).
literal stage: c1sim 'stage' mode = run literally to the first K-moment whose champion process (R1-R3, d >= 4) leaves the
cap; jump: structural (all R1-R3; tokens ~1 mod 3 nearer than the first non-1-mod-3 token are cleared to D1, that token
is borrowed down to its floor 0/2/3, or the left end is reached), new accumulator = a representative of the deep residue
class r* (mod M) -- deep = at least one borrow at depth >= DEEP; otherwise fail loudly.
usage: python myfol.py B [--rep 2539] [--stages 400] [--start "tokens"]"""
import sys, argparse, os
os.environ.setdefault('C1EXE', 'c1sim2.exe')
import c1lib
DEEP = 20
def rle(v): return c1lib.tok_rle(v)
def jump(toks):
    """toks farthest-first incl a, r (r is the CURRENT accumulator, a representative).  returns (new toks, info)"""
    r = toks[-1]; a = toks[-2]; digs = toks[:-2]
    if a % 3 != 1: raise RuntimeError(f'a-token {a} not 1 mod 3')
    if r % 3 != 1: raise RuntimeError(f'accumulator {r} not 1 mod 3')
    # nearest-first scan
    j = len(digs) - 1; nz = 0
    while j >= 0 and digs[j] % 3 == 1 and digs[j] >= 1:
        j -= 1
    # tokens digs[j+1:] are all ~1 mod 3: they are cleared to 1; digs[j] is the blocker (or j = -1: left end)
    cleared = digs[j + 1:]
    nonzero = [i for i, x in enumerate(cleared) if x != 1]
    if j >= 0:
        T = digs[j]
        if T in (0, 2, 3): Tf = T; borrowed = False
        else: Tf = 3 if T % 3 == 0 else 2; borrowed = True
        ev = 'block'
    else:
        Tf = None; borrowed = False; ev = 'left'
    # depth of the deepest borrow: a borrow from cleared token at index i (farthest-first within cleared) happens at depth
    # (len(cleared) - 1 - i) zeros nearer... the deepest borrow source is the farthest non-1 token (or T if borrowed)
    if borrowed: depth = len(cleared)
    elif nonzero: depth = len(cleared) - 1 - nonzero[0]
    else: depth = -1
    if depth < DEEP: raise RuntimeError(f'shallow jump (depth {depth}): {rle(toks)}')
    new = (digs[:j] + [Tf] if j >= 0 else []) + [1] * len(cleared) + [1, None]
    return new, dict(ev=ev, depth=depth)
def follow(start_bits, head, state, rep, stages, log):
    bits, h, q = start_bits, head, state
    for s in range(stages):
        line = c1lib.stage(bits, h, q)
        f = line.split()
        if f[0] == 'HALT':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]} minpos={f[5]}'); return 'HALT'
        if f[0] != 'J':
            log(f'{s} FAIL {line}'); return 'FAIL'
        i1 = line.index('|'); i2 = line.index('|', i1 + 1)
        toks = [int(x) for x in line[i1 + 1:i2].split()]
        log(f'{s} K: {rle(toks[:-2])} | a={toks[-2]} r={toks[-1]}  (step {f[1]})')
        new, info = jump(toks)
        new[-1] = rep
        log(f'{s} J: ev={info["ev"]} depth={info["depth"]} -> {rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        bits = c1lib.word(new); h = len(bits); q = 'G'
    return 'MAXSTAGES'
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b', type=int); ap.add_argument('--rep', type=int, default=2539)
    ap.add_argument('--stages', type=int, default=400); ap.add_argument('--log', default=None)
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None
    def log(x):
        print(x, flush=True)
        if lf: lf.write(x + '\n'); lf.flush()
    w = c1lib.kstart(a.b)
    log(f'c1 from K(0^35;0;{a.b}), rep {a.rep}')
    log('RESULT ' + follow(w, len(w), 'G', a.rep, a.stages, log))
