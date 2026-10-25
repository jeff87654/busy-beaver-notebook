"""proto1 semantic check: original Cantor-stack RM (zf2 DAG) vs the new register-stack RM (zf2s DAG, Q op),
both executed symbolically (symrm.py: pair/unpair/if_eq/move loops accelerated, Big = structural Cantor trees).

usage: python semcheck.py ORIG.tm NEW.tm ITERS TRIALS [seed]
 (1) ITERS consecutive main() iterations from the boot state (all registers 0; the new RM gets the full
     201-run boot register file, junk run of value 1 at index 68).  After every iteration compare
       halt flag, prooflist, nextproof, axiomcode, param1..3, topwff/top, stack contents, scratch1..3,
     where orig stack = unpack(wffstack) and new stack = R[11 : 11+depth] (trailing zeros stripped on both),
     and check that the new RM's untouched tail R[11+depth:] equals the boot R[11:] (no underflow into boot runs).
 (2) TRIALS random single-iteration trials from random states (random wff stacks, random padding of the new
     stack with zero entries counted by depth, random axiom codes incl. matching DET premises / halting cases)."""
import sys, os, random, ctypes
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
from symrm import SymRM, cpair, cunpair, isz, add
import semtest_gen as G


class SymRMS(SymRM):
    """SymRM with the proto1 Q op on a dynamic register list."""
    def __init__(self, path):
        super().__init__(path)
        self.nq = [0, 0]

    def run_edge(self, e, R):
        if e[0] == 'op' and e[2] == 'q':
            self.ops += 1
            r = self.ri(e[1])
            if isz(R[r + 1]):
                R[r] = add(R[r], 3); del R[r + 1]; self.nq[0] += 1
            else:
                R.insert(r + 1, 0); self.nq[1] += 1
            return ('N',)
        return super().run_edge(e, R)


def unpack(ws):
    out = []
    while not isz(ws):
        x, ws = cunpair(ws); out.append(x)
    return out


def strip(l):
    l = list(l)
    while l and isz(l[-1]): l.pop()
    return l


def boot_rf():
    R = [0] * 201; R[68] = 1; return R


def ostate(O, R):
    i = O.regidx
    return dict(pl=R[i['prooflist']], np=R[i['nextproof']], ac=R[i['axiomcode']],
                p=(R[i['param1']], R[i['param2']], R[i['param3']]), top=R[i['topwff']],
                stack=strip(unpack(R[i['wffstack']])),
                scratch=[R[i[s]] for s in ('scratch1', 'scratch2', 'scratch3')])


def nstate(N, R):
    i = N.regidx; d = R[i['depth']]; T = i['top']
    return dict(pl=R[i['prooflist']], np=R[i['nextproof']], ac=R[i['axiomcode']],
                p=(R[i['param1']], R[i['param2']], R[i['param3']]), top=R[T],
                stack=strip(R[T + 1:T + 1 + d]),
                scratch=[R[i[s]] for s in ('scratch1', 'scratch2', 'scratch3')])


def main():
    orig, new, iters, trials = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    O = SymRM(orig); N = SymRMS(new)
    assert N.regidx['top'] == 10 and N.regidx['second'] == 11 and N.regidx['depth'] == 9, N.regidx
    # ---- (1) consecutive iterations from boot ----
    RO = [0] * O.nreg; RN = boot_rf(); tail0 = boot_rf()[11:]
    bad = 0; maxdepth = 0; it = -1; so = {'np': 0, 'stack': []}
    for it in range(iters):
        ho = O.main(RO); hn = N.main(RN)
        so, sn = ostate(O, RO), nstate(N, RN)
        d = RN[9]; maxdepth = max(maxdepth, d)
        tail_ok = RN[11 + d:] == tail0
        if ho != hn or so != sn or not tail_ok:
            bad += 1
            if bad <= 3:
                print('ITER MISMATCH', it, ho, hn, '\n orig', so, '\n new ', sn, '\n tail_ok', tail_ok)
        if ho or hn:
            print('halt at iteration', it, ho, hn); break
    print(f'(1) {it + 1} consecutive iterations from boot: mismatches {bad}; final nextproof {so["np"]}, '
          f'theorem-stack depth {RN[9]} (max {maxdepth}), orig stack len {len(so["stack"])}, '
          f'Q merges/inserts {N.nq}, symbolic ops orig {O.ops} new {N.ops}', flush=True)
    # ---- (2) random single iterations ----
    rng = random.Random(seed); bad2 = 0; sel = Counter(); nh = 0; skipped = 0
    for t in range(trials):
        st, extra = G.random_state(rng)
        pl, np, tw, wslist = st
        R1 = [0] * O.nreg; i = O.regidx
        R1[i['prooflist']], R1[i['nextproof']], R1[i['topwff']] = pl, np, tw
        ws = 0
        for x in reversed(wslist): ws = cpair(x, ws)
        R1[i['wffstack']] = ws
        R2 = boot_rf(); j = N.regidx
        R2[j['prooflist']], R2[j['nextproof']], R2[j['top']] = pl, np, tw
        pad = wslist + [0] * extra['zpad']
        R2[j['depth']] = len(pad)
        R2[11:11] = pad
        for r in ('axiomcode', 'param1', 'param2', 'param3'):
            v = rng.randrange(0, 5); R1[i[r]] = v; R2[j[r]] = v
        try:
            h1 = O.main(R1)
        except ValueError:
            skipped += 1; continue      # symbolic engine cannot represent this case
        h2 = N.main(R2)
        s1, s2 = ostate(O, R1), nstate(N, R2)
        d = R2[9]; tail_ok = R2[11 + d:] == boot_rf()[11:]
        sel[extra['ac']] += 1; nh += h1
        if h1 != h2 or (not h1 and (s1 != s2 or not tail_ok)):
            bad2 += 1
            if bad2 <= 3: print('TRIAL MISMATCH', t, extra, h1, h2, '\n orig', s1, '\n new ', s2, tail_ok)
    print(f'(2) {trials} random single-iteration trials ({skipped} skipped): mismatches {bad2}; '
          f'halting cases {nh}; axiom codes tried {dict(sorted(sel.items()))}')
    return bad + bad2


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
