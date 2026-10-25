"""Whole-chain follower for the 1LD1LC machine with an EXPLICIT size ordering of the huge accumulators: the n-th new huge
accumulator is represented by 19 + 2520*rank[n] (residue 19 mod 2520 = the universal class).  Start: the stage-0 output
[9^u 11 1^(2u+35) | 1 | 2] (u = 520 is the real class mod 2520: m = 1075).  Same literal stages (stage35g) and the same
abstract jump (follow2.jump) as ord_run.py; parked tokens are never altered.
usage: python chain.py --u 520 --ranks 1,2,3,4,5,6,7,8,3,4,6 --log FILE"""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/v1LD1LC')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
from lit1 import run, rle, fmt, M
import mf35
from follow2 import Aff, Fail, jump
import blk

def follow(u, ranks, stages, maxs, log, start=None):
    E = 1; LB = 19; MM = 2520
    toks = start if start else [9] * u + [11] + [1] * (2 * u + 36)
    a, r = (toks[-2], toks[-1]) if start else (1, 2)
    toks = toks[:-2] if start else toks
    n = 0
    for s in range(stages):
        o = run(toks, a, r, maxs=maxs)
        if o['kind'] == 'H':
            log(f'{s} HALT {o["state"]}{o["read"]} ones={o["ones"]} step={o["step"]}'); return 'HALT', o
        if o['kind'] != 'K':
            log(f'{s} {o["raw"][:100]}'); return o['kind'], o
        if o['far']:
            log(f'{s} FAR JUNK {o["far"][:60]}'); return 'FAR', o
        digits, a, r = o['toks'], o['a'], o['r']
        log(f'{s} K: {blk.fmt(blk.blocks(digits))} | a={a} r={r} step={o["step"]}')
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(a), Aff(1)), ('D', Aff(r), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            log(f'{s} JUMPFAIL {ex}'); return 'FAIL', None
        vals = {}
        for p, v in newp.items():
            if v.exact:
                vals[p] = mf35.rep(v, MM, LB)
            else:
                base = mf35.rep(v, MM, LB)
                if base != LB:
                    log(f'{s} NONUNIVERSAL residue: {v} -> {base}')
                k = ranks[n] if n < len(ranks) else ranks[-1]
                n += 1
                vals[p] = base + MM * k
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz} hd={info.get("huge_depth")} newr={vals} -> {blk.fmt(blk.blocks(new[:-2]))} | a={new[-2]} r={new[-1]}')
        toks, a, r = new[:-2], new[-2], new[-1]
    return 'MAXSTAGES', None

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--u', type=int, default=520)
    ap.add_argument('--ranks', default='1,2,3,4,5,6,7,8,3,4,6')
    ap.add_argument('--stages', type=int, default=40)
    ap.add_argument('--maxs', type=int, default=20_000_000_000)
    ap.add_argument('--log', required=True)
    a = ap.parse_args()
    lf = open(a.log, 'w')
    def log(s):
        lf.write(s + '\n'); lf.flush()
    ranks = [int(x) for x in a.ranks.split(',')]
    k, o = follow(a.u, ranks, a.stages, a.maxs, log)
    log(f'RESULT {k}'); print(a.u, a.ranks, k, (o['ones'] if o and o.get('kind') == 'H' else ''))
