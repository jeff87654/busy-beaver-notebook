"""chain.py: mini-follower chain for n1 from the real start with a SIZE-ORDERED representative policy:
the accumulators that later become parked tokens (the ones produced by clearing a 2R+3 token, i.e. the jump right
after a growth stage: R1- and R4-type) get a big representative 19 + 2520*bigk; all others get 19.  This is the
real size order (parked token >> the accumulator that meets it).  --policy std gives the selector's run.
usage: python chain.py --b0 6 --stages 60 --bigk 1 --log F"""
import sys, argparse, threading
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
from follow2 import Aff, Fail, jump
from st import N1, rle
ap = argparse.ArgumentParser()
ap.add_argument('--b0', type=int, default=6)
ap.add_argument('--stages', type=int, default=60)
ap.add_argument('--bigk', type=int, default=1)
ap.add_argument('--maxs', type=float, default=4e8)
ap.add_argument('--log', default=None)
ap.add_argument('--policy', default='ordered')
a = ap.parse_args()
lf = open(a.log, 'w') if a.log else None


def log(s):
    print(s, flush=True)
    if lf:
        lf.write(s + '\n')
        lf.flush()


F = mf35g.FAMILIES['GH']
E = 1
LB = 19
MM = 2520
word, head, state = mf35g.xstart('GH', a.b0)
sys.setrecursionlimit(30000)


def run():
    global word, head, state
    for s in range(a.stages):
        out = mf35g.run_stage('GH', N1, word, head, state, int(a.maxs))
        f = out.split()
        if not f:
            log(f'{s} FAIL no output')
            return
        if f[0] == 'H':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]}')
            return
        if f[0] in ('T', 'W'):
            log(f'{s} {f[0]} {out[:100]}')
            return
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        log(f'{s} K: {rle(digits)} | a={toks[1]} r={toks[0]}' + (f' far[{len(far)}]' if far else ''))
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
            log(f'{s} JUMPFAIL {ex}')
            return
        nz = 0
        for m in digits[::-1]:
            if m != 1:
                break
            nz += 1
        tokbefore = digits[-nz - 1] if nz < len(digits) else None
        big = (tokbefore is not None and tokbefore % 3 == 2 and tokbefore > 3) if a.policy == 'ordered' else False
        vals = {}
        for p, v in newp.items():
            base = mf35.rep(v, MM, LB)
            vals[p] = base if v.exact else (base + MM * a.bigk if big else base)
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 20000:
            new[-1] = LB + ((new[-1] - LB) % MM)
        nz2 = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz2 += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz2} newr={",".join(f"{p}={v}" for p, v in vals.items())} '
            f'big={big} -> {rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
    log('MAXSTAGES')


threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=run)
t.start()
t.join()
