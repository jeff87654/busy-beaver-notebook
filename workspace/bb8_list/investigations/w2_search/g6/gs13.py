"""gs13.py: lazy TNF enumeration of 11-13-state extensions of G6 through the REAL-START follower (std world, b0 = 6).

Entry: one defined G6 transition X keeps its write/move but goes to the new state K.  K, L, M and J1 are free and are
branched lazily (write x move x next-state, TNF on the new states) whenever the follower's literal stage reads them.
Constraint: round 1 (stages 0 .. EXH-1, before G6's first exhaustion stage) must reproduce G6's stage tokens exactly
(far bits may differ: a flag written left of the list is allowed).  From stage EXH on anything goes.
Leaves: HALT@stage (undefined-slot halts; those at stage >= EXH are the interesting ones), DIFF@stage (pruned in round 1),
T/W/FAIL, ALIVE (no halt within MAXST stages).
usage: python gs13.py OUT.tsv [--entries A0,B1,..] [--nnew 3] [--maxst 80] [--maxnodes N]"""
import sys, os, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g6lib
from g6lib import run_stage, rle, word_of_tokens, Q, SUF, E
from follow2 import Aff, Fail, jump
import mf35

G6 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---'
ST = 'ABCDEFGHIJKLM'
EXH = 26          # G6's first exhaustion stage in the std world (b0 = 6)


def mstr(sl, n):
    return '_'.join(sl[2 * q] + sl[2 * q + 1] for q in range(n))


def jump_next(toks, far):
    """follower jump from a K-moment (std policy); returns (word, info) or raises"""
    digits = toks[2:][::-1]
    ent = []
    for m in digits:
        if ent and ent[-1][1] == m:
            ent[-1][2] += 1
        else:
            ent.append(['D', m, 1])
    left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
    items, newp, info = jump(left, [], {}, E)
    vals = {p: mf35.rep(v, 2520, 19) for p, v in newp.items()}
    new = []
    for e in items:
        m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
        c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
        new += [m] * c
    if len(new) >= 2 and new[-1] > 2000:
        new[-1] = 19 + ((new[-1] - 19) % 2520)
    return far + word_of_tokens(new) + SUF, info.get('event')


def reference(maxst):
    word, head, state = g6lib.xstart(6)
    ref = []
    for s in range(maxst):
        out, _ = run_stage(G6, word, head, state, 200_000_000)
        parts = out.split('|'); toks = [int(x) for x in parts[1].split()]; far = parts[2].strip() if len(parts) > 2 else ''
        ref.append((tuple(toks), far, int(out.split()[1])))
        word, ev = jump_next(toks, far); head, state = len(word), Q
    return ref


class Search:
    def __init__(self, out, nnew, maxst, maxnodes, maxs):
        self.out = out; self.nnew = nnew; self.maxst = maxst; self.maxnodes = maxnodes; self.maxs = maxs
        self.ref = reference(EXH)
        self.nodes = 0; self.stats = {}; self.nodes_entry0 = 0

    def leaf(self, kind, sl, n, s, extra=''):
        self.stats[kind] = self.stats.get(kind, 0) + 1
        if kind not in ('DIFF', 'DIFF0'):
            self.out.write(f'{mstr(sl, n)}\t{kind}\t{s}\t{extra}\n'); self.out.flush()

    def options(self, n):
        # n = number of states currently in the machine string; a slot may target A..(n-1) or introduce state n
        nmax = min(n + 1, 10 + self.nnew)
        return [f'{w}{d}{ST[q]}' for w in '01' for d in 'LR' for q in range(nmax)]

    def run(self, sl, n, s, word, head, state, hist):
        """follow from stage s with the given stage input"""
        while True:
            self.nodes += 1
            if self.nodes - self.nodes_entry0 > self.maxnodes:
                self.stats['CAP'] = self.stats.get('CAP', 0) + 1
                return
            m = mstr(sl, n)
            out, used = run_stage(m, word, head, state, 2 * self.ref[s][2] + 20000 if s < EXH else self.maxs)
            f = out.split()
            if not f:
                self.leaf('FAIL', sl, n, s, 'no output'); return
            if f[0] == 'H':
                slot = f[2] + f[3]
                i = 2 * ST.index(f[2]) + int(f[3])
                if s >= 20:
                    self.leaf('HALT', sl, n, s, f'{slot} ones={f[4]} ' + ';'.join(hist[-3:]))
                else:
                    self.stats['HALT<20'] = self.stats.get('HALT<20', 0) + 1
                # branch (only free slots can be undefined)
                for v in self.options(n):
                    sl2 = list(sl); sl2[i] = v
                    q = ST.index(v[2]); n2 = n
                    if q >= n:
                        n2 = q + 1; sl2 += ['---', '---']
                    self.run(sl2, n2, s, word, head, state, hist)
                return
            if f[0] in ('T', 'W'):
                self.leaf(f[0], sl, n, s, ';'.join(hist[-3:])); return
            parts = out.split('|'); toks = [int(x) for x in parts[1].split()]; far = parts[2].strip() if len(parts) > 2 else ''
            if s < EXH and tuple(toks) != self.ref[s][0]:
                self.leaf('DIFF0' if s == 0 else 'DIFF', sl, n, s); return
            try:
                word, ev = jump_next(toks, far)
            except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
                self.leaf('FAIL', sl, n, s, str(ex)[:60]); return
            h = f'{s}:{rle(toks[2:][::-1])[:40]}|{toks[1]}|{toks[0]}' + (f' far{len(far)}' if far else '') + f' ev={ev}'
            hist = hist + [h]
            head, state = len(word), Q
            s += 1
            if s >= self.maxst:
                self.leaf('ALIVE', sl, n, s, ';'.join(hist[-2:])); return


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--entries', default=None)
    ap.add_argument('--nnew', type=int, default=3); ap.add_argument('--maxst', type=int, default=80)
    ap.add_argument('--maxnodes', type=int, default=10**7); ap.add_argument('--maxs', type=int, default=30_000_000)
    a = ap.parse_args()
    base = g6lib.slots_of(G6)
    entries = a.entries.split(',') if a.entries else [ST[q] + str(c) for q in range(10) for c in (0, 1) if base[2 * q + c] != '---']
    with open(a.out, 'w') as out:
        S = Search(out, a.nnew, a.maxst, a.maxnodes, a.maxs)
        for x in entries:
            i = 2 * ST.index(x[0]) + int(x[1])
            sl = list(base) + ['---', '---']
            sl[i] = sl[i][:2] + 'K'
            t0 = time.time(); n0 = S.nodes; st0 = dict(S.stats); S.nodes_entry0 = S.nodes
            S.run(sl, 11, 0, *g6lib.xstart(6), [])
            d = {k: v - st0.get(k, 0) for k, v in S.stats.items() if v != st0.get(k, 0)}
            print(f'entry {x}: nodes {S.nodes - n0} {d} {time.time() - t0:.0f}s', flush=True)
        print('TOTAL nodes', S.nodes, S.stats)


if __name__ == '__main__':
    import threading
    sys.setrecursionlimit(60000); threading.stack_size(256 * 1024 * 1024 - 4096)
    t = threading.Thread(target=main); t.start(); t.join()
