"""tcyc.py: translated-cycler check from the champion's literal halting configuration.
  python tcyc.py MACHINES.txt STARTS.txt [STEPS=300000]
Record moments: the head reaches a new rightmost (or leftmost) cell.  For two record moments t1 < t2 on the same side
with the same state, let m = the farthest the head went back (away from that side) during [t1, t2].  If the tape
segment from m to the head at t1 equals the segment from m+d to the head at t2 (d = shift), and everything beyond the
head is blank (true at a record), the run repeats forever shifted by d: translated cycler, never halts.
Snapshots keep K = 4000 cells; a pair whose excursion exceeds K is not decided.  Prints TC / HALT / UNKNOWN."""
import sys
sys.path.insert(0, '.')
from kcls import parse
K = 4000
def check(M, word, head, q, N):
    t = parse(M); L = 1 << 21; off = L // 2
    tape = bytearray(L); tape[off:off+len(word)] = bytes(int(c) for c in word)
    h = off + head; hi = max(h, off + len(word)); lo = min(h, off); n = 0
    recs = {}   # (q, side) -> list of [t1, h1, snapshot, farthest-back position]
    while n < N:
        c = tape[h]; tr = t[2*q + c]
        if tr is None: return 'HALT@%d' % n
        tape[h] = tr[0]; h += tr[1]; q = tr[2]; n += 1
        if h <= K + 2 or h >= L - K - 3: return 'WALL'
        for lst in recs.values():
            for r in lst:
                if r[4] == 1: r[3] = min(r[3], h)
                else: r[3] = max(r[3], h)
        side = 1 if h > hi else (-1 if h < lo else 0)
        if side:
            if side == 1: hi = h
            else: lo = h
            key = (q, side)
            lst = recs.setdefault(key, [])
            for r in lst:
                t1, h1, snap, far, sd = r
                ext = (h1 - far) if side == 1 else (far - h1)
                if ext >= K: continue
                d = h - h1
                if side == 1: a, b2 = snap[K - ext:], bytes(tape[h - ext: h + 1])
                else: a, b2 = snap[:ext + 1], bytes(tape[h: h + ext + 1])
                if a == b2: return 'TC(period %d, shift %d, at %d)' % (n - t1, d, n)
            snap = bytes(tape[h - K: h + 1]) if side == 1 else bytes(tape[h: h + K + 1])
            lst.append([n, h, snap, h, side])
            if len(lst) > 8: lst.pop(0)
    return 'UNKNOWN'
if __name__ == '__main__':
    ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
    starts = [l.split() for l in open(sys.argv[2]) if l.strip()]
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 300000
    for M in ms:
        print(M + '\t' + '\t'.join('%s:%s' % (s[0], check(M, s[1], int(s[2]), ord(s[3]) - 65, N)) for s in starts)); sys.stdout.flush()
