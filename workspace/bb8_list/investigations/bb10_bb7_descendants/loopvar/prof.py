"""prof.py MACHINE WORD STATE SPLIT TOTAL : transition counts before SPLIT (handler) and SPLIT..TOTAL (champion phase); head starts
right of the word (on a blank)."""
import sys, collections
def parse(m):
    t = {}
    for s, g in enumerate(m.split('_')):
        for c in (0, 1):
            x = g[3*c:3*c+3]
            if x[0] != '-': t[(s, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return t
def run(m, w, q, split, total):
    t = parse(m)
    tape = bytearray(4_000_000); off = 2_000_000
    for i, ch in enumerate(w): tape[off+i] = int(ch)
    pos = off + len(w); q = ord(q) - 65
    u1, u2 = collections.Counter(), collections.Counter()
    for st in range(total):
        c = tape[pos]
        if (q, c) not in t: return u1, u2, ('halt', st, chr(65+q)+str(c))
        (u1 if st < split else u2)[chr(65+q)+str(c)] += 1
        wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
    return u1, u2, None
if __name__ == '__main__':
    m, w, q, split, total = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    u1, u2, h = run(m, w, q, split, total)
    print('handler:', ' '.join(f'{k}:{v}' for k, v in sorted(u1.items())))
    print('champion:', ' '.join(f'{k}:{v}' for k, v in sorted(u2.items())))
    print('handler-only:', sorted(set(u1) - set(u2)), 'champion-only:', sorted(set(u2) - set(u1)), h)
