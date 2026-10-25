"""Visit-to-visit rewriting patterns at the tape level.
For consecutive C-visits (head right of word), strip the common LEFT prefix of the two tape words, tokenise the
remains from the head end (pairs: 11=S, 10=A, 01=a), and print (rle shape) -> (rle shape) with counts."""
import sys, itertools, collections
from subr import visits

def tk(u):
    # tokenise from the right end in pairs of tape cells; leftover (odd) cell kept raw at the left
    out = []; i = len(u)
    while i >= 2:
        out.append({'11': 'S', '10': 'A', '01': 'a', '00': 'z'}[u[i-2:i]]); i -= 2
    out.reverse()
    return (u[:i] if i else '') , out

def rl(t):
    return [(k, len(list(g))) for k, g in itertools.groupby(t)]

def pat(w1, w2):
    p = 0
    while p < min(len(w1), len(w2)) and w1[p] == w2[p]: p += 1
    # back up to keep alignment: start the compare window so that the tokenisation from the right is unaffected
    u1, u2 = w1[p:], w2[p:]
    return p, u1, u2

collect = collections.defaultdict(list)
def feed(ds, a, b, maxsteps=400000, maxvis=300):
    vs = visits(ds, a, b, maxsteps, maxvis)
    for (s1, w1), (s2, w2) in zip(vs, vs[1:]):
        if w1 == 'HALT' or w2 == 'HALT': continue
        p, u1, u2 = pat(w1, w2)
        l1, t1 = tk(u1); l2, t2 = tk(u2)
        r1, r2 = rl(t1), rl(t2)
        key = (l1, tuple(k for k, n in r1), l2, tuple(k for k, n in r2))
        collect[key].append((tuple(n for k, n in r1) + tuple(n for k, n in r2), s2 - s1))

if __name__ == '__main__':
    for ds in [(), (1,), (2,), (1, 1), (0, 2), (1, 0, 1), (0, 0, 1), (2, 0, 0, 1), (0,), (0, 0)]:
        for a in (0, 1, 2, 3):
            for b in (0, 1, 2, 3, 4):
                feed(ds, a, b)
    for key, v in sorted(collect.items(), key=lambda kv: -len(kv[1])):
        l1, k1, l2, k2 = key
        print('%-6s %-24s -> %-6s %-24s  n=%d  e.g. %s' % (l1, ' '.join(k1), l2, ' '.join(k2), len(v), v[:2]))
