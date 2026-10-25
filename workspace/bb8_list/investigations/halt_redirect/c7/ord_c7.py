"""Fable's verbose / ordered-representative follower for the GH 0LH machine.
Same loop as mf35g.follow (family GH) but:
  --policy std    : every huge accumulator -> rep 19 (R mod 2520 class, like the lead's runs)
  --policy big    : every huge accumulator -> rep 19 + 2520*BIGK
  --policy floor  : standard reps, but any token whose value exceeds the floor F is kept above F (a parked huge token is
                    never exhausted: whenever the literal stage drives it below F it is lifted by a multiple of 2520)
  --policy order  : the n-th new huge accumulator gets 19 + 2520*min(n, cap)
Prints every stage: the full token list (RLE, farthest first), event, zeros, new accumulator rep."""
import sys, argparse, threading
sys.setrecursionlimit(200000); threading.stack_size(512 * 1024 * 1024)
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf'); sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/c7')
FAM_M = {}
import c7fam, mf35g, mf35
from follow2 import Aff, Fail, jump

M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF_------_------'
FAM = 'C7'

def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)

def follow(b0, policy, stages, maxs, bigk=1, floor=1000, cap=3, log=print, start=None, FAM=None, M=None):
    FAM = FAM or globals()['FAM']; M = M or globals()['M']
    F = mf35g.FAMILIES[FAM]; E = F['E']; LB = 18 + E; MM = 2520
    if start:
        word = mf35.word_of_tokens(start) + F['SUF']; head, state = len(word), F['Q']
    else:
        word, head, state = mf35g.xstart(FAM, b0)
    nparam = 0
    tokens_prev = None
    for s in range(stages):
        out = mf35g.run_stage(FAM, M, word, head, state, maxs)
        if not out:
            log(f'{s} FAIL no output'); return 'FAIL'
        f = out.split()
        if f[0] == 'H':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]}'); return 'HALT'
        if f[0] in ('T', 'W'):
            log(f'{s} {f[0]} {out[:100]}'); return f[0]
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        # literal stage output (the K-moment): digits + a + r
        log(f'{s} K: {rle(digits)} | a={toks[1]} r={toks[0]}' + (f' far={far}' if far else ''))
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
            log(f'{s} JUMPFAIL {ex}'); return 'FAIL'
        vals = {}
        for p, v in newp.items():
            if v.exact:
                vals[p] = mf35.rep(v, MM, LB)
            else:
                nparam += 1
                base = mf35.rep(v, MM, LB)
                if policy == 'std':
                    vals[p] = base
                elif policy == 'big':
                    vals[p] = base + MM * bigk
                elif policy == 'order':
                    vals[p] = base + MM * min(nparam, cap)
                elif policy == 'floor':
                    vals[p] = base + MM * bigk
                elif policy == 'shrink':
                    vals[p] = base + MM * bigk          # current accumulator: window [19+2520*bigk, +2520)
                else:
                    raise ValueError(policy)
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 2000 and policy == 'std':
            new[-1] = LB + ((new[-1] - LB) % MM)
        lifted = []
        if policy == 'shrink':
            # parked tokens (everything but r) are kept small: [19, 2539) with the residue mod 2520 preserved;
            # r (exact large or huge) is kept in the window [19+2520*bigk, +2520): the real regime r >> parked
            for i in range(len(new) - 1):
                if new[i] > 2539:
                    new[i] = LB + ((new[i] - LB) % MM); lifted.append(i)
            if new[-1] > 2000:
                new[-1] = LB + ((new[-1] - LB) % MM) + MM * bigk
        if policy == 'floor':
            for i in range(len(new) - 2):
                if 200 < new[i] < floor:      # a formerly huge token driven down: lift it back (same residue)
                    new[i] += MM * ((floor - new[i] + MM - 1) // MM); lifted.append(i)
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz} newr={",".join(f"{p}={v}" for p, v in vals.items())} '
            f'hd={info.get("huge_depth")} -> {rle(new[:-2])} | a={new[-2]} r={new[-1]}' + (f' lifted={lifted}' if lifted else ''))
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
    return 'MAXSTAGES'

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--b0', type=int, default=6)
    ap.add_argument('--policy', default='std')
    ap.add_argument('--stages', type=int, default=400)
    ap.add_argument('--maxs', type=int, default=200_000_000)
    ap.add_argument('--bigk', type=int, default=1)
    ap.add_argument('--floor', type=int, default=1000)
    ap.add_argument('--cap', type=int, default=3)
    ap.add_argument('--log', default=None)
    ap.add_argument('--start', default=None, help='token list incl. a and r, e.g. "3 41 0 1 5059"')
    ap.add_argument('--machine', default=None)
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None
    def log(s):
        print(s, flush=True)
        if lf: lf.write(s + '\n'); lf.flush()
    def _main():
        r = follow(a.b0, a.policy, a.stages, a.maxs, a.bigk, a.floor, a.cap, log, [int(x) for x in a.start.split()] if a.start else None, M=(a.machine + '_------' * (9 - a.machine.count('_'))) if a.machine else None)
        log(f'RESULT {r}')
    t = threading.Thread(target=_main); t.start(); t.join()
